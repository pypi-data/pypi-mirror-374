use std::cmp::max;
use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::io::Write;
use std::ops::Deref;
use std::path::PathBuf;
use std::rc::Rc;
use std::sync::Arc;

use anyhow::{Context, Result};
use futures::stream::{FuturesUnordered, StreamExt};
use owo_colors::{OwoColorize, Style};
use rand::SeedableRng;
use rand::prelude::{SliceRandom, StdRng};
use rustc_hash::{FxHashMap, FxHashSet};
use tokio::io::AsyncWriteExt;
use tokio::sync::Semaphore;
use tracing::{debug, trace};
use unicode_width::UnicodeWidthStr;

use constants::env_vars::EnvVars;

use crate::cli::reporter::{HookInitReporter, HookInstallReporter};
use crate::cli::run::keeper::WorkTreeKeeper;
use crate::cli::run::{CollectOptions, FileFilter, collect_files};
use crate::cli::{ExitStatus, RunExtraArgs};
use crate::config::{Language, Stage};
use crate::fs::{CWD, Simplified};
use crate::hook::{Hook, InstalledHook};
use crate::printer::{Printer, Stdout};
use crate::run::{CONCURRENCY, USE_COLOR};
use crate::store::{STORE, Store};
use crate::workspace::Project;
use crate::{git, warn_user};

enum HookToRun {
    Skipped(Arc<Hook>),
    ToRun(Arc<InstalledHook>),
}

impl Deref for HookToRun {
    type Target = Hook;

    fn deref(&self) -> &Self::Target {
        match self {
            HookToRun::Skipped(hook) => hook,
            HookToRun::ToRun(hook) => hook,
        }
    }
}

#[allow(clippy::too_many_arguments, clippy::fn_params_excessive_bools)]
pub(crate) async fn run(
    config: Option<PathBuf>,
    hook_ids: Vec<String>,
    hook_stage: Stage,
    from_ref: Option<String>,
    to_ref: Option<String>,
    all_files: bool,
    files: Vec<String>,
    directories: Vec<String>,
    last_commit: bool,
    show_diff_on_failure: bool,
    extra_args: RunExtraArgs,
    verbose: bool,
    printer: Printer,
) -> Result<ExitStatus> {
    // Convert `--last-commit` to `HEAD~1..HEAD`
    let (from_ref, to_ref) = if last_commit {
        (Some("HEAD~1".to_string()), Some("HEAD".to_string()))
    } else {
        (from_ref, to_ref)
    };

    // Prevent recursive post-checkout hooks.
    if hook_stage == Stage::PostCheckout
        && EnvVars::is_set(EnvVars::PREK_INTERNAL__SKIP_POST_CHECKOUT)
    {
        return Ok(ExitStatus::Success);
    }

    let should_stash = !all_files && files.is_empty() && directories.is_empty();

    // Check if we have unresolved merge conflict files and fail fast.
    if should_stash && git::has_unmerged_paths().await? {
        writeln!(
            printer.stderr(),
            "{}: You have unmerged paths. Resolve them before running prek",
            "error".red().bold(),
        )?;
        return Ok(ExitStatus::Failure);
    }

    let mut project = Project::from_config_file_or_directory(config, &CWD)?;
    if should_stash && git::file_not_staged(project.config_file()).await? {
        writeln!(
            printer.stderr(),
            "{}: prek configuration file is not staged, run `{}` to stage it",
            "error".red().bold(),
            format!("git add {}", project.config_file().user_display()).cyan(),
        )?;
        return Ok(ExitStatus::Failure);
    }

    let store = STORE.as_ref()?;
    let reporter = HookInitReporter::from(printer);

    let lock = store.lock_async().await?;

    let hook_ids = hook_ids.into_iter().collect::<BTreeSet<_>>();

    let hooks = project.init_hooks(store, Some(&reporter)).await?;
    let filtered_hooks: Vec<_> = hooks
        .into_iter()
        .filter(|h| hook_ids.is_empty() || hook_ids.contains(&h.id) || hook_ids.contains(&h.alias))
        .filter(|h| h.stages.contains(hook_stage))
        .map(Arc::new)
        .collect();

    if filtered_hooks.is_empty() {
        if hook_ids.is_empty() {
            writeln!(
                printer.stderr(),
                "{}: No hooks found for stage `{}`",
                "error".red().bold(),
                hook_stage.cyan()
            )?;
        } else if hook_ids.len() == 1 {
            writeln!(
                printer.stderr(),
                "{}: No hook found with id `{}` in stage `{}`",
                "error".red().bold(),
                hook_ids.iter().next().unwrap().cyan(),
                hook_stage.cyan()
            )?;
        } else {
            writeln!(
                printer.stderr(),
                "{}: No hooks found with ids {} in stage `{}`",
                "error".red().bold(),
                hook_ids
                    .iter()
                    .map(|id| format!("`{}`", id.cyan()))
                    .collect::<Vec<_>>()
                    .join(", "),
                hook_stage.cyan()
            )?;
        }
        return Ok(ExitStatus::Failure);
    } else if !hook_ids.is_empty() {
        // Warn about hook IDs that don't match any hooks
        let matched_ids: BTreeSet<String> = filtered_hooks
            .iter()
            .flat_map(|h| [h.id.clone(), h.alias.clone()])
            .collect();

        let unmatched_ids: Vec<&String> = hook_ids
            .iter()
            .filter(|id| !matched_ids.contains(*id))
            .collect();

        if !unmatched_ids.is_empty() {
            warn_user!(
                "Ignored non-existent hook ID{}: {}",
                if unmatched_ids.len() > 1 { "s" } else { "" },
                unmatched_ids
                    .iter()
                    .map(|id| format!("`{}`", id.yellow()))
                    .collect::<Vec<_>>()
                    .join(", ")
            );
        }
    }

    let skips = get_skips();
    let skips = filtered_hooks
        .iter()
        .filter(|h| skips.contains(&h.id) || skips.contains(&h.alias))
        .map(|h| h.idx)
        .collect::<FxHashSet<_>>();
    let to_run = filtered_hooks
        .iter()
        .filter(|h| !skips.contains(&h.idx))
        .cloned()
        .collect::<Vec<_>>();

    debug!(
        "Hooks going to run: {:?}",
        to_run.iter().map(|h| &h.id).collect::<Vec<_>>()
    );
    let reporter = HookInstallReporter::from(printer);
    let mut installed_hooks = install_hooks(to_run, store, &reporter).await?;

    // Release the store lock.
    drop(lock);

    let hooks = filtered_hooks
        .into_iter()
        .map(|h| {
            if skips.contains(&h.idx) {
                HookToRun::Skipped(h)
            } else {
                // Find and remove the matching resolved hook
                let idx = installed_hooks
                    .iter()
                    .position(|r| r.idx == h.idx)
                    .expect("Resolved hook must exist");
                HookToRun::ToRun(Arc::new(installed_hooks.swap_remove(idx)))
            }
        })
        .collect::<Vec<_>>();

    // Clear any unstaged changes from the git working directory.
    let mut _guard = None;
    if should_stash {
        _guard = Some(WorkTreeKeeper::clean(store).await?);
    }

    set_env_vars(from_ref.as_ref(), to_ref.as_ref(), &extra_args);

    let filenames = collect_files(CollectOptions {
        hook_stage,
        from_ref,
        to_ref,
        all_files,
        files,
        directories,
        commit_msg_filename: extra_args.commit_msg_filename.clone(),
    })
    .await?;

    let filter = FileFilter::new(
        &filenames,
        project.config().files.as_ref(),
        project.config().exclude.as_ref(),
    );
    trace!("Files after filtered: {}", filter.len());

    run_hooks(
        &hooks,
        &filter,
        store,
        project.config().fail_fast.unwrap_or(false),
        show_diff_on_failure,
        verbose,
        printer,
    )
    .await
}

// `pre-commit` sets these environment variables for other git hooks.
fn set_env_vars(from_ref: Option<&String>, to_ref: Option<&String>, args: &RunExtraArgs) {
    unsafe {
        std::env::set_var("PRE_COMMIT", "1");

        if let Some(ref source) = args.prepare_commit_message_source {
            std::env::set_var("PRE_COMMIT_COMMIT_MSG_SOURCE", source.clone());
        }
        if let Some(ref object) = args.commit_object_name {
            std::env::set_var("PRE_COMMIT_COMMIT_OBJECT_NAME", object.clone());
        }
        if let Some(from_ref) = from_ref {
            std::env::set_var("PRE_COMMIT_ORIGIN", from_ref.clone());
            std::env::set_var("PRE_COMMIT_FROM_REF", from_ref.clone());
        }
        if let Some(to_ref) = to_ref {
            std::env::set_var("PRE_COMMIT_SOURCE", to_ref.clone());
            std::env::set_var("PRE_COMMIT_TO_REF", to_ref.clone());
        }
        if let Some(ref upstream) = args.pre_rebase_upstream {
            std::env::set_var("PRE_COMMIT_PRE_REBASE_UPSTREAM", upstream.clone());
        }
        if let Some(ref branch) = args.pre_rebase_branch {
            std::env::set_var("PRE_COMMIT_PRE_REBASE_BRANCH", branch.clone());
        }
        if let Some(ref branch) = args.local_branch {
            std::env::set_var("PRE_COMMIT_LOCAL_BRANCH", branch.clone());
        }
        if let Some(ref branch) = args.remote_branch {
            std::env::set_var("PRE_COMMIT_REMOTE_BRANCH", branch.clone());
        }
        if let Some(ref name) = args.remote_name {
            std::env::set_var("PRE_COMMIT_REMOTE_NAME", name.clone());
        }
        if let Some(ref url) = args.remote_url {
            std::env::set_var("PRE_COMMIT_REMOTE_URL", url.clone());
        }
        if let Some(ref checkout) = args.checkout_type {
            std::env::set_var("PRE_COMMIT_CHECKOUT_TYPE", checkout.clone());
        }
        if args.is_squash_merge {
            std::env::set_var("PRE_COMMIT_SQUASH_MERGE", "1");
        }
        if let Some(ref command) = args.rewrite_command {
            std::env::set_var("PRE_COMMIT_REWRITE_COMMAND", command.clone());
        }
    }
}

fn get_skips() -> Vec<String> {
    match EnvVars::var_os(EnvVars::SKIP) {
        Some(s) if !s.is_empty() => s
            .to_string_lossy()
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect(),
        _ => vec![],
    }
}

pub async fn install_hooks(
    hooks: Vec<Arc<Hook>>,
    store: &Store,
    reporter: &HookInstallReporter,
) -> Result<Vec<InstalledHook>> {
    let num_hooks = hooks.len();
    let mut installed_hooks = Vec::with_capacity(hooks.len());
    let store_hooks = Rc::new(store.installed_hooks().collect::<Vec<_>>());

    // Group hooks by language to enable parallel installation across different languages.
    let mut hooks_by_language = FxHashMap::default();
    for hook in hooks {
        hooks_by_language
            .entry(hook.language)
            .or_insert_with(Vec::new)
            .push(hook);
    }

    let mut futures = FuturesUnordered::new();
    let semaphore = Arc::new(Semaphore::new(*CONCURRENCY));

    for (_, hooks) in hooks_by_language {
        let semaphore = semaphore.clone();
        let partitions = partition_hooks(&hooks);

        for hooks in partitions {
            let semaphore = semaphore.clone();
            let store_hooks = store_hooks.clone();

            futures.push(async move {
                let mut hook_envs = Vec::with_capacity(hooks.len());
                let mut newly_installed = Vec::new();

                for hook in hooks {
                    // Find a matching installed hook environment.
                    if let Some(info) = store_hooks
                        .iter()
                        .chain(newly_installed.iter().filter_map(|h| {
                            if let InstalledHook::Installed { info, .. } = h {
                                Some(info)
                            } else {
                                None
                            }
                        }))
                        .find(|info| info.matches(&hook))
                    {
                        debug!(
                            "Found installed environment for hook `{}` at `{}`",
                            &hook,
                            info.env_path.display()
                        );
                        hook_envs.push(InstalledHook::Installed {
                            hook,
                            info: info.clone(),
                        });
                        continue;
                    }

                    let _permit = semaphore.acquire().await.unwrap();
                    debug!("No matching environment found for hook `{hook}`, installing...");

                    let installed_hook = hook
                        .language
                        .install(hook.clone(), store, reporter)
                        .await
                        .context(format!("Failed to install hook `{hook}`"))?;

                    installed_hook
                        .mark_as_installed(store)
                        .await
                        .context(format!("Failed to mark hook `{hook}` as installed"))?;

                    match &installed_hook {
                        InstalledHook::Installed { info, .. } => {
                            debug!("Installed hook `{hook}` in `{}`", info.env_path.display());
                        }
                        InstalledHook::NoNeedInstall { .. } => {
                            debug!("Hook `{hook}` does not need installation");
                        }
                    }

                    newly_installed.push(installed_hook);
                }

                // Add newly installed hooks to the list.
                hook_envs.extend(newly_installed);
                anyhow::Ok(hook_envs)
            });
        }
    }

    while let Some(result) = futures.next().await {
        installed_hooks.extend(result?);
    }
    reporter.on_complete();

    debug_assert_eq!(
        num_hooks,
        installed_hooks.len(),
        "Number of hooks installed should match the number of hooks provided"
    );

    Ok(installed_hooks)
}

/// Partition hooks into groups where hooks in the same group have same dependencies.
/// Hooks in different groups can be installed in parallel.
fn partition_hooks(hooks: &[Arc<Hook>]) -> Vec<Vec<Arc<Hook>>> {
    if hooks.is_empty() {
        return vec![];
    }

    let n = hooks.len();
    let mut visited = vec![false; n];
    let mut groups = Vec::new();

    // DFS to find all connected sets
    #[allow(clippy::items_after_statements)]
    fn dfs(
        index: usize,
        hooks: &[Arc<Hook>],
        visited: &mut [bool],
        current_group: &mut Vec<usize>,
    ) {
        visited[index] = true;
        current_group.push(index);

        for i in 0..hooks.len() {
            if !visited[i] && hooks[index].dependencies() == hooks[i].dependencies() {
                dfs(i, hooks, visited, current_group);
            }
        }
    }

    // Find all connected components
    for i in 0..n {
        if !visited[i] {
            let mut current_group = Vec::new();
            dfs(i, hooks, &mut visited, &mut current_group);

            // Convert indices back to actual sets
            let group_sets: Vec<Arc<Hook>> = current_group
                .into_iter()
                .map(|idx| hooks[idx].clone())
                .collect();

            groups.push(group_sets);
        }
    }

    groups
}

struct StatusPrinter {
    printer: Printer,
    columns: usize,
}

impl StatusPrinter {
    const PASSED: &'static str = "Passed";
    const FAILED: &'static str = "Failed";
    const SKIPPED: &'static str = "Skipped";
    const NO_FILES: &'static str = "(no files to check)";
    const UNIMPLEMENTED: &'static str = "(unimplemented yet)";

    fn for_hooks(hooks: &[HookToRun], printer: Printer) -> Self {
        let columns = Self::calculate_columns(hooks);
        Self { printer, columns }
    }

    fn calculate_columns(hooks: &[HookToRun]) -> usize {
        let name_len = hooks
            .iter()
            .map(|hook| hook.name.width_cjk())
            .max()
            .unwrap_or(0);
        max(
            80,
            name_len + 3 + Self::NO_FILES.len() + 1 + Self::SKIPPED.len(),
        )
    }

    fn write_skipped(
        &self,
        hook_name: &str,
        reason: &str,
        style: Style,
    ) -> Result<(), std::fmt::Error> {
        let dots = self.columns - hook_name.width_cjk() - Self::SKIPPED.len() - reason.len() - 1;
        let line = format!(
            "{hook_name}{}{}{}",
            ".".repeat(dots),
            reason,
            Self::SKIPPED.style(style)
        );
        writeln!(self.printer.stdout(), "{line}")
    }

    fn write_running(&self, hook_name: &str) -> Result<(), std::fmt::Error> {
        write!(
            self.printer.stdout(),
            "{}{}",
            hook_name,
            ".".repeat(self.columns - hook_name.width_cjk() - Self::PASSED.len() - 1)
        )
    }

    fn write_passed(&self) -> Result<(), std::fmt::Error> {
        writeln!(self.printer.stdout(), "{}", Self::PASSED.on_green())
    }

    fn write_failed(&self) -> Result<(), std::fmt::Error> {
        writeln!(self.printer.stdout(), "{}", Self::FAILED.on_red())
    }

    fn stdout(&self) -> Stdout {
        self.printer.stdout()
    }
}

/// Run all hooks.
async fn run_hooks(
    hooks: &[HookToRun],
    filter: &FileFilter<'_>,
    store: &Store,
    fail_fast: bool,
    show_diff_on_failure: bool,
    verbose: bool,
    printer: Printer,
) -> Result<ExitStatus> {
    let printer = StatusPrinter::for_hooks(hooks, printer);
    let mut success = true;

    let mut diff = git::get_diff().await?;
    // Hooks might modify the files, so they must be run sequentially.
    for hook in hooks {
        let (hook_success, new_diff) =
            run_hook(hook, filter, store, diff, verbose, &printer).await?;

        success &= hook_success;
        diff = new_diff;
        let fail_fast = fail_fast
            || match hook {
                HookToRun::Skipped(_) => false,
                HookToRun::ToRun(hook) => hook.fail_fast,
            };
        if !success && fail_fast {
            break;
        }
    }

    if !success && show_diff_on_failure {
        writeln!(printer.stdout(), "All changes made by hooks:")?;
        let color = if *USE_COLOR {
            "--color=always"
        } else {
            "--color=never"
        };
        git::git_cmd("git diff")?
            .arg("--no-pager")
            .arg("diff")
            .arg("--no-ext-diff")
            .arg(color)
            .check(true)
            .spawn()?
            .wait()
            .await?;
    }

    if success {
        Ok(ExitStatus::Success)
    } else {
        Ok(ExitStatus::Failure)
    }
}

/// Shuffle the files so that they more evenly fill out the xargs
/// partitions, but do it deterministically in case a hook cares about ordering.
fn shuffle<T>(filenames: &mut [T]) {
    const SEED: u64 = 1_542_676_187;
    let mut rng = StdRng::seed_from_u64(SEED);
    filenames.shuffle(&mut rng);
}

async fn run_hook(
    hook: &HookToRun,
    filter: &FileFilter<'_>,
    store: &Store,
    diff: Vec<u8>,
    verbose: bool,
    printer: &StatusPrinter,
) -> Result<(bool, Vec<u8>)> {
    let hook = match hook {
        HookToRun::Skipped(hook) => {
            printer.write_skipped(&hook.name, "", Style::new().black().on_yellow())?;
            return Ok((true, diff));
        }
        HookToRun::ToRun(hook) => hook,
    };

    let mut filenames = filter.for_hook(hook);

    if filenames.is_empty() && !hook.always_run {
        printer.write_skipped(
            &hook.name,
            StatusPrinter::NO_FILES,
            Style::new().black().on_cyan(),
        )?;
        return Ok((true, diff));
    }

    if !Language::supported(hook.language) {
        printer.write_skipped(
            &hook.name,
            StatusPrinter::UNIMPLEMENTED,
            Style::new().black().on_yellow(),
        )?;
        return Ok((true, diff));
    }

    printer.write_running(&hook.name)?;
    std::io::stdout().flush()?;

    let start = std::time::Instant::now();

    let filenames = if hook.pass_filenames {
        shuffle(&mut filenames);
        filenames
    } else {
        vec![]
    };

    let (status, output) = hook
        .language
        .run(hook, &filenames, store)
        .await
        .context(format!("Failed to run hook `{hook}`"))?;

    let duration = start.elapsed();

    let new_diff = git::get_diff().await?;
    let file_modified = diff != new_diff;
    let success = status == 0 && !file_modified;
    if success {
        printer.write_passed()?;
    } else {
        printer.write_failed()?;
    }

    if verbose || hook.verbose || !success {
        writeln!(
            printer.stdout(),
            "{}",
            format!("- hook id: {}", hook.id).dimmed()
        )?;
        if verbose || hook.verbose {
            writeln!(
                printer.stdout(),
                "{}",
                format!("- duration: {:.2?}s", duration.as_secs_f64()).dimmed()
            )?;
        }
        if status != 0 {
            writeln!(
                printer.stdout(),
                "{}",
                format!("- exit code: {status}").dimmed()
            )?;
        }
        if file_modified {
            writeln!(
                printer.stdout(),
                "{}",
                "- files were modified by this hook".dimmed()
            )?;
        }

        // To be consistent with pre-commit, merge stderr into stdout.
        let stdout = output.trim_ascii();
        if !stdout.is_empty() {
            if let Some(file) = hook.log_file.as_deref() {
                let mut file = fs_err::tokio::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(file)
                    .await?;
                file.write_all(stdout).await?;
                file.sync_all().await?;
            } else {
                writeln!(
                    printer.stdout(),
                    "{}",
                    textwrap::indent(&String::from_utf8_lossy(stdout), "  ").dimmed()
                )?;
            }
        }
    }

    Ok((success, new_diff))
}
