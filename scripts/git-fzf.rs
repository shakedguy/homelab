use std::collections::hash_map::DefaultHasher;
use std::env;
use std::fmt::Write as FmtWrite;
use std::fs;
use std::hash::{Hash, Hasher};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug)]
struct Cache {
    refs_mtime: u64,
    head_mtime: u64,
    include_remotes: bool,
    entries: Vec<String>,
}

fn git_output(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    if !out.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn git_dir() -> Option<PathBuf> {
    git_output(&["rev-parse", "--git-dir"]).map(PathBuf::from)
}

fn path_mtime(path: &Path) -> u64 {
    fs::metadata(path)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

fn cache_path(repo_git_dir: &Path) -> PathBuf {
    let mut hasher = DefaultHasher::new();
    repo_git_dir.hash(&mut hasher);
    let key = format!("{:x}", hasher.finish());

    let cache_root = env::var_os("XDG_CACHE_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env::var_os("HOME").unwrap_or_default()).join(".cache"));
    let cache_dir = cache_root.join("git-fzf");
    let _ = fs::create_dir_all(&cache_dir);
    cache_dir.join(format!("{key}.txt"))
}

fn load_cache(path: &Path) -> Option<Cache> {
    let content = fs::read_to_string(path).ok()?;
    let mut lines = content.lines();
    let refs_mtime = lines
        .next()?
        .strip_prefix("refs_mtime:")?
        .parse::<u64>()
        .ok()?;
    let head_mtime = lines
        .next()?
        .strip_prefix("head_mtime:")?
        .parse::<u64>()
        .ok()?;
    let include_remotes = lines
        .next()?
        .strip_prefix("include_remotes:")?
        .trim()
        == "1";
    // skip optional blank line
    let entries: Vec<String> = lines.map(|s| s.to_string()).collect();
    Some(Cache {
        refs_mtime,
        head_mtime,
        include_remotes,
        entries,
    })
}

fn save_cache(path: &Path, cache: &Cache) {
    let mut buf = String::new();
    let _ = write!(
        &mut buf,
        "refs_mtime:{}\nhead_mtime:{}\ninclude_remotes:{}\n",
        cache.refs_mtime,
        cache.head_mtime,
        if cache.include_remotes { 1 } else { 0 }
    );
    for line in &cache.entries {
        buf.push_str(line);
        buf.push('\n');
    }
    let _ = fs::write(path, buf);
}

fn collect_branches(include_remotes: bool) -> Vec<String> {
    let mut refs = vec!["refs/heads"];
    if include_remotes {
        refs.push("refs/remotes");
    }
    let mut args = vec![
        "for-each-ref",
        "--sort=-committerdate",
        "--format=%(refname:short)\t%(objectname:short)\t%(committerdate:relative)\t%(authorname)",
    ];
    args.extend(refs.iter().copied());
    git_output(&args)
        .map(|out| out.lines().map(|s| s.to_string()).collect())
        .unwrap_or_default()
}

fn main() {
    let repo_git_dir = match git_dir() {
        Some(p) => p,
        None => return,
    };

    let refs_mtime = path_mtime(&repo_git_dir.join("refs"));
    let head_mtime = path_mtime(&repo_git_dir.join("HEAD"));
    let include_remotes = env::var("GIT_FZF_INCLUDE_REMOTES")
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false);

    let cpath = cache_path(&repo_git_dir);
    let mut entries: Vec<String> = Vec::new();
    if let Some(cache) = load_cache(&cpath) {
        if cache.refs_mtime == refs_mtime
            && cache.head_mtime == head_mtime
            && cache.include_remotes == include_remotes
        {
            entries = cache.entries;
        }
    }

    if entries.is_empty() {
        entries = collect_branches(include_remotes);
        save_cache(
            &cpath,
            &Cache {
                refs_mtime,
                head_mtime,
                include_remotes,
                entries: entries.clone(),
            },
        );
    }

    if !entries.is_empty() {
        println!("{}", entries.join("\n"));
    }
}

