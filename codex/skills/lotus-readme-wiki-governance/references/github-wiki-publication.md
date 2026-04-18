# GitHub Wiki Publication

Use this reference when the task includes publishing a Lotus repo wiki to GitHub.

## Source Of Truth

Publication rules are strict:

1. author and review pages in the repository under `wiki/`,
2. treat `wiki/` as the canonical authored source,
3. treat the GitHub wiki repo as a publish target only,
4. do not maintain two live authored copies.

## Normal Publication Flow

1. verify the repo-local `wiki/` source is the version you want to publish,
2. verify the GitHub wiki remote exists,
3. clone the GitHub wiki repo into a disposable publish location,
4. replace its page set from the repo-local `wiki/` source,
5. commit with a truthful publication message,
6. push the wiki repo,
7. keep the repository commit history separate from the GitHub wiki publication history.

## Windows-Safe Fallback

Some older GitHub wikis contain page filenames that cannot be checked out on Windows because they
use characters such as `:`.

When that happens:

1. do not weaken the repo-local `wiki/` source to match the broken historical filenames,
2. do not skip publication,
3. use a bare clone of the `*.wiki.git` repository,
4. stage the repo-local `wiki/` files into that bare clone with `--work-tree`,
5. commit and push from the bare clone.

This keeps publication working even when the historical live wiki is not Windows-safe.

## Legacy Wiki Replacement

When an old wiki exists:

1. read it only for durable signal,
2. classify what still belongs to the current repository,
3. rewrite retained meaning in current Lotus language and architecture terms,
4. publish the new governed page set,
5. let the publish remove stale legacy page files that no longer belong.

Do not preserve stale page names or stale ownership claims just to avoid deleting old wiki files.

## Publication Outcome

After publish, record:

1. the local repository commit that owns the `wiki/` source, if one was created,
2. the GitHub wiki commit that was pushed,
3. whether the local repository is ahead of remote because the source commit has not been pushed yet,
4. whether the live wiki now matches the repo-local source.
