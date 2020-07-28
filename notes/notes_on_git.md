# Notes on Git

# Git Internals

## Git Object Types

Git **objects** are the actual data of Git, the main thing that the repository is made up of. All of these types of objects are stored in the Git Object Database, which is kept in the Git Directory. Git objects are immutable. Each object is compressed (with `zlib`) and referenced by the **SHA-1** value of its contents plus a small header. They are stored in the `.git/objects/` directory.

There are four object types in Git:

1. **Blob**. In Git, the contents of files are stored as **blobs**. It is important to note that it is the *contents* that are stored, not the files. The names and modes of the files are not stored with the blob, just the contents. Therefore a blob object is nothing but a chunk of binary data. It doesn't refer to anything else or have attributes of any kind, not even a file name.

![](https://i.imgur.com/U8PkBvd.png)

2. **Tree**. Directories in Git basically correspond to **trees**. A tree is a simple list of trees and blobs that the tree contains, along with the names and modes of those trees and blobs. The contents section of a tree object consists of a simple text file that lists the: i) *mode*, ii) *type*, iii) *name* and iv) *SHA* of each entry.

![](https://i.imgur.com/Sa5cA9i.png)

3. **Commit**. The **commit** object is very simple, much like the tree. It simply points to a tree and keeps: i) *tree* ii) *author*, iii) *committer*, iv) *message* and v) any *parent commits* that directly preceded it. Most times a commit will only have a single parent but e.g. if you merge two branches, the next commit will point to both of them.

![](https://i.imgur.com/dgbdfRB.png)

4. **Tag (annotated)**. The annotated **tag** is an object that provides a permanent shorthand name for a particular commit. It contains an i) *object*, ii) *type*, iii) *tag name*, iv) *tagger* and v) *message*. Normally the type is commit and the object is the SHA-1 of the commit you 're tagging. This tag can also be GPG signed, providing cryptographic integrity to a release or version. Note that *annotated* tags are different from *lightweight* tags (see [Git References](#git-references)).

![](https://i.imgur.com/brljv1N.png)


## Git References

The most direct way to reference a commit is via its **SHA-1** hash. This acts as the unique ID for each commit. It's sometimes necessary to resolve a branch, tag, or another indirect reference into the corresponding commit hash. For this, you can use the `git rev-parse` command.

In addition to the Git objects, which are immutable - that is, they cannot ever be changed, there are **references** (or **refs**) also stored in Git. Unlike the objects, references can constantly change. They are simple pointers to a particular commit, something like a tag, but easily moveable. You can think them as a user-friendly alias for a commit hash. These are stored in the `.git/refs/` directory.

There are three reference types in Git:

1. **Branch**. A **branch** in Git is nothing more than a file in the `.git/refs/heads/` directory that contains the SHA-1 of the most recent commit of that branch. That's basically what a branch in Git is: a simple pointer or reference to the head of a line of work. To branch that line of development, all Git does is create a new file in that directory that points to the same SHA-1. As you continue to commit, one of the branches will keep changing to point to the new commit SHA-1, while the other one can stay where it was.
2. **Tag (lightweight)**. We can also create a tag that doesn't actually add a tag object to the database, but just creates a reference to it in the `.git/refs/tags` directory. That is all a lightweight tag is - a reference that never moves.
	Note that *annotated* tags are meant for release while *lightweight* tags are meant for private or temporary object labels.
3. **Remote reference**. A Git **remote** is a repository that contains the same project as you are working on in your local one, but at a different location. A remote is thus nickname for an external repository that you want to interact with and `origin` is the name Git gives to the original repository when you make a copy of (clone) it. Collaborating with others involves managing these remote repositories and pushing and pulling data to and from them when you need to share work.
	**Remote references** are references (pointers) in your remote repositories, including branches, tags, and so on. You can get a full list of remote references explicitly with `git ls-remote <remote>`, or `git remote show <remote>` for remote branches as well as more information. Nevertheless, a more common way is to take advantage of remote-tracking branches.
	**Remote-tracking branches** are local references to the state of remote branches. You can't move them; Git moves them for you whenever you do any network communication, to make sure they accurately represent the state of the remote repository. Think of them as bookmarks, to remind you where the branches in your remote repositories were the last time you connected to them. Remote-tracking branch names take the form `<remote>/<branch>`. For instance, if you wanted to see what the master branch on your origin remote looked like as of the last time you communicated with it, you would check the `origin/master` branch.
	Remote-tracking branches differ from branches (`refs/heads` references) mainly in that they're considered read-only. You can `git checkout` to one, but Git won't point `HEAD` at one, so you'll never update it with a commit command. Git manages them as bookmarks to the last known state of where those branches were on those servers.

### Special Refs

Git keeps a special pointer called **HEAD** (stored in the file `.git/HEAD`) to keep track of the branch that we are currently on (checked out). Usually the `HEAD` file is a *symbolic* reference i.e. unlike a normal reference, it contains a pointer to another reference.

However in some cases the `HEAD` file may contain the SHA-1 value of a Git object. This happens when you checkout a tag, commit, or remote branch, which puts your repository in "detached HEAD" state. A **detached HEAD** means that `HEAD` is pointing directly to a commit rather than a branch. Any changes that are committed in this state are only remembered as long as you don't switch to a different branch. As soon as you checkout a new branch or tag, the detached commits will be "lost" (because `HEAD` has moved). If you want to save commits done in a detached state, you need to create a branch to remember the commits.

In addition to the `.git/refs/` directory, there are a few special refs that reside in the top-level `.git` directory. For the most part, `HEAD` is the only reference that you'll be using directly. The others are generally only useful when writing lower-level scripts that need to hook into Git's internal workings. These refs are all created and updated by Git when necessary.

- **HEAD**: The currently checked-out commit/branch.
- **FETCH_HEAD**: The most recently fetched branch from a remote repo.
- **ORIG_HEAD**: A backup reference to `HEAD` before drastic changes to it.
- **MERGE_HEAD**: The commit(s) that you're merging into the current branch with git merge.
- **CHERRY_PICK_HEAD**: The commit that you're cherry-picking.

## Git Data Model

The Git object data is a **directed acyclic graph (DAG)**. That is, starting at any commit you can traverse its parents in one direction and there is no chain that begins and ends with the same object. All commit objects point to a tree and optionally to previous commits. All trees point to one or many blobs and/or trees. Given this simple model, we can store and retrieve vast histories of complex trees of arbitrarily changing content quickly and efficiently.

![](https://i.imgur.com/4PexYHC.png)

## The Three Trees of Git

Git as a system manages and manipulates three trees in its normal operation:

| Tree              | Role                              |
| ----------------- | --------------------------------- |
| HEAD              | Last commit snapshot, next parent |
| Index             | Proposed next commit snapshot     |
| Working Directory | Sandbox                           |

1. The `HEAD` is the pointer to the current branch reference, which is in turn a pointer to the last commit made on that branch. That means `HEAD` will be the parent of the next commit that is created. It's helpful to think of `HEAD` as the snapshot of your last commit on that branch.
2. The **Index** is your proposed next commit. This concept is also referred to as Git's **Staging Area** as this is what Git looks at when you run `git commit`.
3. The **Working Directory** (also commonly referred to as the **working tree**). The other two trees store their content in an efficient but inconvenient manner, inside the `.git` folder. The working directory unpacks them into actual files, which makes it much easier for you to edit them. Think of the working directory as a *sandbox*, where you can try changes out before committing them to your *staging area (index)* and then to *history*.
   Git populates this index with a list of all the file contents that were last checked out into your working directory and what they looked like when they were originally checked out. You then replace some of those files with new versions of them, and `git commit` converts that into the tree for a new commit.

Git's typical workflow is to record snapshots of your project in successively better states, by manipulating these three trees.

![](https://i.imgur.com/2HNeG0e.png)

## Specifying Revisions

A revision parameter **\<rev>** typically, but not necessarily, names a commit object. It uses what is called an **extended SHA-1** syntax. Many Git commands can accept special identifiers for commits and (sub)directory trees:

- **Commit-ish** are identifiers that ultimately lead to a commit object, e.g `tag -> commit`.
- **Tree-ish** are identifiers that ultimately lead to tree (i.e. directory) objects, e.g. `tag -> commit -> project-root-directory`.

Because commit objects always point to a directory tree object (the root directory of your project), any identifier that is "commit-ish" is, by definition, also "tree-ish". In other words, any identifier that leads to a commit object can also be used to lead to a (sub)directory tree object. But since directory tree objects never point to commits in Git's versioning system, not every identifier that points to a (sub)directory tree can also be used to point to a commit. In other words, the set of "commit-ish" identifiers is a strict subset of the set of "tree-ish" identifiers.

| Commit-ish/Tree-ish       | Examples                                             |
| ------------------------- | ---------------------------------------------------- |
| 1. `<sha1>`               | `dae86e1950b1277e545cee180551750029cfe735`, `dae86e` |
| 2. `<describeOutput>`     | `v1.7.4.2-679-g3bee7fb`                              |
| 3. `<refname>`            | `master`, `heads/master`, `refs/heads/master`        |
| 4. `<refname>@{<date>}`   | `master@{yesterday}, HEAD@{5 minutes ago}`           |
| 5. `<refname>@{<n>}`      | `master@{1}`                                         |
| 6. `@{<n>}`               | `@{1}`                                               |
| 7. `@{-<n>}   `           | `@{-1}`                                              |
| 8. `<refname>@{upstream}` | `master@{upstream}, @{u}`                            |
| 9. `<rev>^[<n>]`          | `HEAD^, v1.5.1^0`                                    |
| 10. `<rev>~[<n>]`         | `HEAD~, master~3`                                    |
| 11. `<rev>^{<type>}`      | `v0.99.8^{commit}`                                   |
| 12. `<rev>^{}`            | `v0.99.8^{}`                                         |
| 13. `<rev>^{/<text>}`     | `HEAD^{/fix nasty bug}`                              |
| 14. `:/<text>`            | `:/fix nasty bug`                                    |

| Tree-ish only     | Examples                                    |
| ----------------- | ------------------------------------------- |
| 1. `<rev>:<path>` | `HEAD:README`, `:README`, `master:./README` |
| 2. `:<n>:<path>`  | `:0:README`, `:README`                      |


Below is an example illustrating the usage for the `<rev>^[<n>]` and `<rev>~[<n>]` spec. Both commit nodes B and C are parents of commit node A. Parent commits are ordered left-to-right.

```
G   H   I   J
 \ /     \ /
  D   E   F
   \  |  / \
    \ | /   |
     \|/    |
      B     C
       \   /
        \ /
         A

------------------------------------

A =      = A^0
B = A^   = A^1     = A~1
C =      = A^2
D = A^^  = A^1^1   = A~2
E = B^2  = A^^2
F = B^3  = A^^3
G = A^^^ = A^1^1^1 = A~3
H = D^2  = B^^2    = A^^^2  = A~2^2
I = F^   = B^3^    = A^^3^
J = F^2  = B^3^2   = A^^3^2

```

## Specifying Ranges

History traversing commands such as `git log` operate on a set of commits, not just a single commit. For these commands, specifying a single revision, using the notation described in the previous section, means the set of commits reachable from the given commit. A commit's reachable set is the commit itself and the commits in its ancestry chain.

| Range                                     | Explanation                                                                                                                                                                             |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `<rev>`                                | Include commits that are reachable from `<rev>` (i.e. `<rev>` and its ancestors).                                                                                                       |
| 2. `^<rev>`                               | Exclude commits that are reachable from `<rev>` (i.e. `<rev>` and its ancestors).                                                                                                       |
| 3. `<rev1>..<rev2>`                       | Include commits that are reachable from `<rev2>` but exclude those that are reachable from `<rev1>`. When either `<rev1>` or `<rev2>` is omitted, it defaults to `HEAD`.                |
| 4. `<rev1>...<rev2>`                      | Include commits that are reachable from either `<rev1>` or `<rev2>` but exclude those that are reachable from both. When either `<rev1>` or `<rev2>` is omitted, it defaults to `HEAD`. |
| 5. `<rev>^@`, e.g. `HEAD^@`               | A suffix `^` followed by an at sign is the same as listing all parents of `<rev>` (meaning, include anything reachable from its parents, but not the commit itself).                    |
| 6. `<rev>^!`, e.g. `HEAD^!`               | A suffix `^` followed by an exclamation mark is the same as giving commit `<rev>` and then all its parents prefixed with `^` to exclude them (and their ancestors).                     |
| 7. `<rev>^-<n>`, e.g. `HEAD^-`, `HEAD^-2` | Equivalent to `<rev>^<n>..<rev>`, with `<n> = 1` if not given.                                                                                          

## The Reflog

The reflog is Git's safety net. It records almost every change you make in your repository, regardless of whether you committed a snapshot or not. You can think of it as a chronological history of everything you've done in your local repo. Think of the reflog as Git's version of shell history. To view the reflog, run the `git reflog` command. It should output something that looks like the following:

```
400e4b7 HEAD@{0}: checkout: moving from master to HEAD~2
0e25143 HEAD@{1}: commit (amend): Integrate some awesome feature into `master`
00f5425 HEAD@{2}: commit (merge): Merge branch ';feature';
ad8621a HEAD@{3}: commit: Finish the feature
```

This can be translated as follows:

- You just checked out `HEAD~2`.
- Before that you amended a commit message.
- Before that you merged the feature branch into master.
- Before that you committed a snapshot.

The `HEAD{<n>}` syntax lets you reference commits stored in the reflog. It works a lot like the `HEAD~<n>` references from the [Specifying Revisions](#specifying-revisions) section, but the `<n>` refers to an entry in the reflog instead of the commit history. You can use this to revert to a state that would otherwise be lost. For example, lets say you just scrapped a new feature with `git reset`. Your reflog might look something like this:

```
ad8621a HEAD@{0}: reset: moving to HEAD~3
298eb9f HEAD@{1}: commit: Some other commit message
bbe9012 HEAD@{2}: commit: Continue the feature
9cb79fa HEAD@{3}: commit: Start a new feature
```

The three commits before the `git reset` are now dangling, which means that there is no way to reference them, except through the reflog. Now, let's say you realize that you shouldn't have thrown away all of your work. All you have to do is check out the `HEAD@{1}` commit to get back to the state of your repository before you ran `git reset`:

```bash
git checkout HEAD@{1}
```

This puts you in a detached `HEAD` state. From here, you can create a new branch and continue working on your feature.

# Git Commands

## Setting Up a Repository

### `git init`

This command creates an empty Git repository - basically a `.git` directory with subdirectories for objects, refs/heads, refs/tags, and template files. An initial `HEAD` file that references the `HEAD` of the `master` branch is also created. Running `git init` in an existing repository is safe. It will not overwrite things that are already there.

```bash
git init
```

Transform the current directory into a Git repository.

```bash
git init <directory>
```

Create an empty Git repository in the specified directory. Running this command will create a new subdirectory called containing nothing but the `.git` subdirectory.

```bash
git init --bare <directory>
```

Initialize an empty Git repository, but omit the working directory. This is called a **bare** repository. Shared repositories should always be created with the `--bare` flag (see discussion below). Conventionally, repositories initialized with the `--bare` flag end in `.git`.

The `--bare` flag creates a repository that doesn't have a working directory, making it impossible to edit files and commit changes in that repository. You would create a bare repository to `git push` and `git pull` from, but never directly commit to it. Central repositories should always be created as bare repositories because pushing branches to a non-bare repository has the potential to overwrite changes. Think of `--bare` as a way to mark a repository as a storage facility, as opposed to a development environment. This means that for virtually all Git workflows, the central repository is bare, and developers local repositories are non-bare.


### `git clone`

`git clone` is primarily used to point to an existing repo and make a clone or copy of that repo at in a new directory, at another location. The original repository can be located on the local filesystem or on remote machine accessible supported protocols. This command lones a repository into a newly created directory, creates remote-tracking branches for each branch in the cloned repository (visible using `git branch --remotes`), and creates and checks out an initial branch that is forked from the cloned repository's currently active branch.

As a convenience, cloning automatically creates a remote connection called `origin` pointing back to the original repository. This makes it very easy to interact with a central repository. This automatic connection is established by creating Git refs to the remote branch heads under `refs/remotes/origin` and by initializing `remote.origin.url` and `remote.origin.fetch` configuration variables.

```bash
git clone <repo>
```

This will clone the given repository onto a new directory based on the repo's name.

```bash
git clone <repo> <directory>
```

Clone `repo` into the specified `<directory>`.

#### Common Options

- `--bare`: Similar to `git init --bare`, a copy of the remote repository will be made with an omitted working directory. This means that a repository will be set up with the history of the project that can be pushed and pulled from, but cannot be edited directly. In addition, no remote branches for the repo will be configured with the bare repository. Like `git init --bare`, this is used to create a hosted repository that developers will not edit directly.
- `--mirror`: Passing the `--mirror` argument implicitly passes the `--bare` argument as well, resulting in a bare repo with no editable working files. In addition, `--mirror` will clone all the extended refs of the remote repository, and maintain remote branch tracking configuration. You can then run `git remote update` on the mirror and it will overwrite all refs from the origin repo, giving you exact 'mirrored' functionality.
- `-o <name>, --origin <name>`: Instead of using the remote name `origin` to keep track of the upstream repository, use `<name>`.


## Saving Changes

### `git add`

The `git add` command adds a change in the working directory to the staging area.

```bash
git add [<options>] [--] <pathspec>...
```

A **pathspec** is a pattern used to limit paths in Git commands. Pathspecs are used in commands like `git add`, `git grep`, `git diff`, `git checkout` and many others, to limit the scope of operations to some subset of the tree or worktree. Fileglobs (e.g. `*.c`) can be given to add all matching files. Also a leading directory name (e.g. `dir` to add `dir/file1` and `dir/file2`) can be given to update the index to match the current state of the directory as a whole.

#### Common Options

- `-A, --all`: Stage all (new, modified, deleted) files (same as `git add .`).
- `-u, --update`: Update only files being tracked.
- `-i, --interactive`: Interactively pick files to add to the staging area.
- `-p, --patch`: Begin an interactive staging session that lets you choose portions of a file to add to the next commit. This will present you with a chunk of changes and prompt you for a command.

### `git commit`

The `git commit` command captures a snapshot of the project's currently staged changes. Committed snapshots can be thought of as "safe" versions of a project - Git will never change them unless you explicitly ask it to.

```bash
git commit [<options>] [--] [<pathspec>...]
```

This is the general usage of the command. Only the staged changes specified in `pathspec` will be commited. If `pathspec` is omitted, then all staged changes will be commited.

```bash
git commit
```

Commit the staged snapshot. This will launch a text editor prompting you for a commit message. After you've entered a message, save the file and close the editor to create the actual commit.

#### Common Options

- `-a, --all`: Commit a snapshot of all changes in the working directory. This only includes modifications to tracked files (those that have been added with `git add` at some point in their history).
- `-m, --message <message>`: A shortcut command that immediately creates a commit with a passed commit message. Use `git commit -am <message>` to combine the above two options.
- `--amend`: This command is a convenient way to modify the most recent commit. It lets you combine staged changes with the previous commit instead of creating an entirely new commit. It can also be used to simply edit the previous commit message without changing its snapshot.
- `--no-edit`:  Combine the `--amend` with the `--no-edit` flag, to make the amendment to your commit without changing its commit message i.e. `git commit --amend --no-edit`

### `git diff`

Diffing is a function that takes two input data sets and outputs the changes between them. `git diff` is a multi-use Git command that when executed runs a diff function on Git data sources. These data sources can be commits, branches, files and more.

```bash
git diff [<options>] [<commit> [<commit>]] [--] [<path>...]
```

General usage for the command. View the changes in the working tree relative a commit or view the changes between two arbitrary commits. The `<path>` parameter, when given, in used to limit the diff to the named paths.

```bash
git diff
```

By default, `git diff` will show differences between *working directory* and *index*.

```bash
git diff HEAD
```

This will show differences between *working directory* and *HEAD*.

```bash
git diff --staged
```

This will show differences between *index* and *HEAD*.

```bash
git diff master new_branch ./path/to/file
```

`git diff` can be passed Git refs to commits to diff. Some example refs are, HEAD, tags, and branch names. This compares the two branches. The command can also be scoped to a single file adding `./path/to/file`.

![](https://i.imgur.com/fCS7axe.png)

### `git stash`

The `git stash` command takes your uncommitted changes (both staged and unstaged), saves them away for later use, and then reverts them from your working copy. The stash is local to your Git repository; stashes are not transferred to the server when you push. Stashes are actually encoded in your repository as commit objects. The special ref at `.git/refs/stash` points to your most recently created stash, and previously created stashes are referenced by the stash ref's reflog.

#### Sub-Commands

```bash
git stash [push [-p | --patch] [-k | --[no-]keep-index] [-q | --quiet] [-u | --include-untracked] [-a | --all] [-m | --message <message>] [--pathspec-from-file=<file> [--pathspec-file-nul]] [--] [<pathspec>...]]
```

Calling `git stash` without any arguments is equivalent to `git stash push`. Use `git stash` when you want to record the current state of the working directory and the index, but want to go back to a clean working directory.

- `-u, --include-untracked`: Include untracked files in stash.
- `-a, --all`: Include ignored, in addition to untracked files in stash.
- `-m, --message <message>`: A stash is by default listed as "WIP on branchname...", but you can give a more descriptive message.

```bash
git stash (pop | apply) [--index] [-q | --quiet] [<stash>]
```

Popping your stash removes the changes from your stash and reapplies them to your working copy. Alternatively, you can reapply the changes to your working copy and keep them in your stash with `git stash apply`.

```bash
git stash list [<options>]
```

List the stash entries that you currently have. Each stash entry is listed with its name (e.g. `stash@{0}` is the latest entry, `stash@{1}` is the one before, etc.), the name of the branch that was current when the entry was made, and a short description of the commit the entry was based on.

```bash
git stash show [<options>] [<stash>]
```

You can view a summary of a stash with `git stash show`, or pass the `-p` option to view the full diff of a stash.

```bash
git stash drop [-q | --quiet] [<stash>]
git stash clear
```

If you decide you no longer need a particular stash, you can delete it with `git stash drop`, or you can delete all of your stashes with `git stash clear`.

### `gitignore`

A `.gitignore` file specifies intentionally untracked files that Git should ignore. Files already tracked by Git are not affected. Each line in a `.gitignore` file specifies a pattern. The purpose of `.gitignore` files is to ensure that certain files not tracked by Git remain untracked. To stop tracking a file that is currently tracked, use `git rm --cached` (see also [`git rm`](#git-rm)).

## Inspecting a Repository

### `git status`

The `git status` command displays the state of the working directory and the staging area. It lets you see which changes have been staged, which haven't, and which files aren't being tracked by Git.

### `git log`

The `git log` command displays committed snapshots. It lets you list the project history, filter it, and search for specific changes. Log output can be customized in several ways, from simply filtering commits to displaying them in a completely user-defined format.

```bash
git log [<options>] [<revision-range>] [[--] <path>...]
```

General usage of the command. Show only commits in the specified revision range. When no `<revision-range>` is specified, it defaults to `HEAD` (i.e. the whole history leading to the current commit). `origin..HEAD` specifies all the commits reachable from the current commit (i.e. `HEAD`), but not from `origin`(see [Specifying Ranges](#specifying-ranges)). If `<path>` is specified, show only commits that are enough to explain how the files that match the specified paths came to be.

### `git show`

`git show` is a command line utility that is used to view expanded details on Git objects such as blobs, trees, tags, and commits.

```bash
git show [<options>] <object>...
```

It has specific behavior per object type. For commits it shows the log message and textual diff. It also presents the merge commit in a special format as produced by `git diff-tree --cc`. For tags, it shows the tag message and the referenced objects. For trees, it shows the names (equivalent to `git ls-tree --name-only`). For plain blobs, it shows the plain contents. By default, `git show` acts against the `HEAD` reference. 

### `git blame`

The `git blame` command is used to examine the contents of a file line by line and see when each line was last modified and who the author of the modifications was. The output format of git blame can be altered with various command line options.

## Undoing Changes

### `git reset`

The `git reset` command is a complex and versatile tool for undoing changes. At a surface level, `git reset` is similar in behavior to `git checkout`. Where `git checkout` solely operates on the `HEAD` ref pointer, `git reset` will move the `HEAD` ref pointer and the current branch ref pointer.

```bash
git reset [<tree-ish>] [--] <pathspec>...
```

Reset the index entries for all paths that match the `<pathspec>` to their state at `<tree-ish>`. It does not affect the working tree or the current branch. This form does not move the `HEAD`. `git reset <pathspec>` is the opposite of `git add <pathspec>`. This command is equivalent to `git restore [--source=<tree-ish>] --staged <pathspec>...`.

```bash
git reset [--mixed | --soft | --hard | --merge | --keep] [-q] [<commit>]
```

Set the current branch head `HEAD` to `<commit>`, optionally modifying index and working tree to match. The `<tree-ish>`/`<commit>` defaults to `HEAD` in all forms of `git reset`. The default invocation of `git reset` has implicit arguments of `--mixed` and `HEAD` (i.e. is equivalent to`git reset --mixed HEAD`). In this form `HEAD` is the specified commit. Instead of `HEAD` any Git SHA-1 commit hash can be used.

#### Common Options

- `--mixed`: The ref pointers are updated. The index is reset to the state of the specified commit. Any changes that have been undone from the index are moved to the working directory.
- `--soft`: When the `--soft` argument is passed, the ref pointers are updated and the reset stops there. The index and the working directory are left untouched.
- `--hard`: When passed `--hard` the commit history ref pointers are updated to the specified commit. Then, the index and working directory are reset to match that of the specified commit. Any previously pending changes to the index and the working directory gets reset to match the state of the commit tree. This means any pending work that was hanging out in the index and working directory will be lost.
- `-q, --quiet`: Be quiet, only report errors.

![](https://i.imgur.com/Fz2qwx7.png)

### `git clean`

Cleans the working tree by recursively removing files that are not under version control, starting from the current directory. While commands like `git reset` and `git checkout` operate on files previously added to the index, the `git clean` command operates on *untracked* files. Untracked files are files that have been created within your repo's working directory but have not yet been added to the repository's tracking index using the `git add` command.

#### Common Options

- `-n, --dry-run`: Don't actually remove anything, just show what would be done.
- `-f, --force`: This option initiates the actual deletion of untracked files from the current directory. Force is required unless the `clean.requireForce` configuration option is set to false. This will not remove untracked folders or files specified by `.gitignore`.
- `-d`: This option tells `git clean` that you also want to remove any untracked directories, by default it will ignore directories.
- `-i, --interactive`: Show what would be done and clean files interactively.

### `git revert`

The `git revert` command can be considered an 'undo' type command, however, it is not a traditional undo operation. Instead of removing the commit from the project history, it figures out how to invert the changes introduced by the commit and appends a new commit with the resulting inverse content. This prevents Git from losing history, which is important for the integrity of your revision history and for reliable collaboration. A revert operation will take the specified commit, inverse the changes from that commit, and create a new "revert commit". The ref pointers are then updated to point at the new revert commit making it the tip of the branch.

```bash
git revert [options] <commit>...
```

General use of the command. Given one or more existing commits, revert the changes that the related patches introduce, and record some new commits that record them. This requires your working tree to be clean (no modifications from the HEAD commit).

```bash
git revert HEAD
```

Git revert expects a commit ref was passed in and will not execute without one. Here we have passed in the `HEAD` ref. This will revert the latest commit.

#### Common Options

- `-e, --edit`: This is the default option and will open the configured system editor and prompts you to edit the commit message prior to committing the revert.
- `--no-edit`: This is the inverse of the `-e` option. The revert will not open the editor.
- `-n, --no-commit`: Passing this option will prevent `git revert` from creating a new commit that inverses the target commit. Instead of creating the new commit this option will add the inverse changes to the index and working directory.

The `git revert` command is a forward-moving undo operation that offers a safe method of undoing changes.

### `git rm`

Removes files matching `<pathspec>` from the index, or from the working directory and the index. It can be thought of as the inverse of the `git add` command. There is no option to remove a file from just the working directory.

```bash
git rm [-f | --force] [-n] [-r] [--cached] [--ignore-unmatch] [--quiet] [--pathspec-from-file=<file> [--pathspec-file-nul]] [--] [<pathspec>...]
```

Specifies the target files to remove. The option value can be an individual file, a space delimited list of files `file1 file2 file3`, or a wildcard file glob `(~./directory/*)`.

#### Common Options

- `-n, --dry-run`: This option is a safeguard that will execute the `git rm` command but not actually delete the files. Instead it will output which files it would have removed.
- `-f, --force]`: This option is used to override the safety check that Git makes to ensure that the files in `HEAD` match the current content in the staging index and working directory. It explicitly removes the target files from both the working directory and staging index.
- `-r`: This is shorthand for 'recursive'. When operating in recursive mode `git rm` will remove a target directory and all the contents of that directory.
- `--cached`: Use this option to unstage and remove paths only from the index. Working tree files, whether modified or not, will be left alone.

Executing `git rm` is not a permanent update. The command will update the staging index and the working directory. These changes will not be persisted until a new commit is created and the changes are added to the commit history. This means that the changes here can be "undone" using common Git commands.

### `git restore`

Restore specified paths in the working tree with some contents from a restore source. If a path is tracked but does not exist in the restore source, it will be removed to match the source.

```bash
git restore [<options>] [-s <tree> | --source=<tree>] [-S | --staged] [-W | --worktree] [--] <pathspec>...
```

#### Common Options

- `-s <tree>, --source=<tree>`: Restore the working tree files with the content from the given tree. It is common to specify the source tree by naming a commit, branch or tag associated with it. If not specified, the default restore source for the working tree is the index, and the default restore source for the index is `HEAD`.
- `-W, --worktree | -S, --staged`: Specify the restore location. If neither option is specified, by default the working tree is restored. Specifying `--staged` will only restore the index. Specifying both restores both. When both `--staged` and `--worktree` are specified, `--source` must also be specified.

## Using Branches

### `git branch`

The `git branch` command lets you create, list, rename, and delete branches. It doesn't let you switch between branches or put a forked history back together again.

```bash
git branch
```

List local branches in your repository. This is synonymous with `git branch --list`.

- `-r, --remote`: List remote branches.
- `-a, --all`: List all branches, including local and remote branches.
- `-v, --verbose`: Show SHA-1 and commit subject line for each head.
- `-vv`: Show relationship to upstream branch, in addition to the info displayed with `-v`.

```bash
git branch <branchname> [<start-point>]
```

Create a new branch called `<branchname>` which points to the current `HEAD`, or `<start-point>` if given. This does *not* check out the new branch.

```bash
git branch [-d | --delete] <branchname>
git branch -D <branchname>
```

- `-d, --delete`: Delete the specified branch. This is a "safe" operation in that Git prevents you from deleting the branch if it has unmerged changes.
- `-D`: Force delete the specified branch, even if it has unmerged changes. This is the command to use if you want to permanently throw away all of the commits associated with a particular line of development.

```bash
git branch [-m | --move] [<oldbranch>] <newbranch>
git branch -M [<oldbranch>] <newbranch>
```

- `-m, --move`: Rename the current branch, or the `<oldbranch>` if specified, to `<newbranch>`.
- `-M`: If `<newbranch>` exists, `-M` must be used to force the rename to happen. In this case `oldbranch` is removed.

```bash
git branch [-f | --force] <branchname> <commit>
```

Move `<branchname>` so that it points to `<commit>`. 

#### Types of Branches

Based on the location of the branch, branches can be categorized into two groups: 

1. **Local Branches**: Branches on a local machine.
2. **Remote Branches**: Branches on a remote machine.

The refs for local branches are stored in the `.git/refs/heads/`. Executing the `git branch` command will output a list of the local branch refs. Remote branches are just like local branches, except they map to commits from somebody else's repository and are prefixed by the remote they belong to, so that you don't mix them up with local branches. Like local branches, Git also has refs for remote branches, which live in the `.git/refs/remotes/` directory.

Depending on their relationship with other branches, they can be further categorized into two groups:

1. **Tracking Branches**: Branches that are associated with other branches on local or remote machines and track their progress. Usually these are local branches that are associated with remote branches, and are referred to as **tracking branches** or **remote tracking branches**. The remote branches that they are tracking are called **upstream branches**.
2. **Non-Tracking Branches**: These are normal branches that are not associated with any other branch.

Tracking branches (see also [Git References](#git-references)) are local branches that have a direct relationship to a remote branch. If you're on a tracking branch and type `git pull`, Git automatically knows which server to fetch from and which branch to merge in. A tracking branch can be created with `git branch --track` or `git checkout -b --track`. The remote branch that is tracked from a local tracking branch is called an **upstream branch**. When you have a tracking branch set up, you can reference its upstream branch with the `@{upstream}` or `@{u}` shorthand (e.g. `git merge @{u}` instead of `git merge origin/master`).

For example, when we clone a repository Git's clone command automatically names it `origin`, pulls down all its data, creates a pointer to where its `master` branch is, and names it `origin/master` locally. Git also gives you your own local master branch starting at the same place as origin's master branch, so you have something to work from. In this case we have configured three branches:

1. The `master` local branch.
2. The `origin/master` (local) tracking branch that tracks the remote branch `master`.
3. The `master` remote branch (or upstream branch) which is located in the remote repository.

```bash
git branch <branchname> --track <remote>/<branchname>
```

When creating a new branch, set up `branch.<name>.remote` and `branch.<name>.merge` configuration entries to mark the start-point branch as "upstream" from the new branch. This configuration will tell Git to show the relationship between the two branches in `git status` and `git branch -v`. Furthermore, it directs `git pull` without arguments to pull from the upstream when the new branch is checked out. You would use `--track` when you create a new branch to track an existing remote branch. If no `<branchname>` is specified, then it defaults to the current branch.

```bash
git branch <branchname> [-u <upstream> | --set-upstream-to=<upstream>]
```

Set up an existing `<branchname>`'s tracking information so `<upstream>` is considered `<branchname>`'s upstream branch. If no `<branchname>` is specified, then it defaults to the current branch. Both switches (`--track` and `set-upstream-to`) can also be used to track local branches.

Τo operate further on the resulting branches the `git branch` command is commonly used with other commands like `git checkout`, `git switch` and `git merge`. Note that the `-f` or `--force` switch can be used to force creation, move/rename, deletion of branches and can also be used with `git checkout` and `git switch`. 

### `git checkout`

The `git checkout` command lets you navigate between the branches created by `git branch`. Checking out a branch updates the files in the working directory to match the version stored in that branch, and tells Git to record all new commits on that branch. Checking out branches is similar to checking out old commits and files in that the working directory is updated to match the selected branch/revision; however, new changes are saved in the project history - that is, it's *not* a read-only operation.

```bash
git checkout <branch>
```

Executing this will switch branches, pointing `HEAD` to the tip of `<branch>`. Local modifications to the files in the working tree and index are kept, so that they can be committed to `<branch>`.

- `-f, --force`: When switching branches, proceed even if the index or the working tree differs from `HEAD`. This is used to throw away local changes.
- `-m, --merge`: When switching branches, if you have local modifications to one or more files that are different between the current branch and the branch to which you are switching, the command refuses to switch branches in order to preserve your modifications in context. However, with this option, a three-way merge between the current branch, your working tree contents, and the new branch is done, and you will be on the new branch.

```bash
git checkout -b <new-branch>
```

The above command simultaneously creates and checks out `<new-branch>`.

```bash
git checkout -b <new-branch> <existing-branch>
```

By default, `git checkout -b` will base the `<new-branch>` off the current `HEAD`. In the above example, `<existing-branch>` is passed which then bases `<new-branch>` off of `<existing-branch>` instead of the current `HEAD`. Instead of `<existing-branch>`, any commit SHA-1 can be used to base off the new branch.

```bash
git checkout -b <branch> --track <remote>/<branch>
```

When creating a new branch, set up "upstream" configuration (see `--track` in [`git branch`](#git-branch)). When executing `git checkout <branch>`, if `<branch>` is not found but there does exist a tracking branch in exactly one remote (call it `<remote>`) with a matching name and `--no-guess` is not specified, treat as equivalent to the above command.

```bash
git checkout [options] [<tree-ish>] [--] <pathspec>...
```

Overwrite the contents of the files that match the pathspec. When the `<tree-ish>` (most often a commit) is not given, overwrite working tree with the contents in the index. When the `<tree-ish>` is given, overwrite both the index and the working tree with the contents at the `<tree-ish>`.

#### Argument Disambiguation

When there is only one argument given and it is not `--` (e.g. `git checkout abc`), and when the argument is both a valid `<tree-ish>` (e.g. a branch `abc` exists) and a valid `<pathspec>` (e.g. a file or a directory whose name is `abc` exists), Git would usually ask you to disambiguate. Because checking out a branch is so common an operation, however, `git checkout abc` takes `abc` as a `<tree-ish>` in such a situation. Use `git checkout -- <pathspec>` (i.e. `git checkout -- abc`), if you want to checkout these paths out of the index.

In summation, `git checkout` bit of a swiss army knife in that has several uses. It can be used to create branches, switch branches, checkout local/remote branches and restore files from commits or the index.

### `git switch`

Switch to a specified branch. The working tree and the index are updated to match the branch. All new commits will be added to the tip of this branch. This command is similar to `git checkout` but has more narrow scope in its usage.

```bash
git switch <branch>
```

Switch current branch to `<branch>`.

```bash
git switch -c <new-branch>
```

Create and switch to a new branch named `<new-branch>` (similar behavior as `git checkout -b`).

```bash
git switch [-m | --merge] <branch>
```

Similar to `git checkout -m`, with this option, a three-way merge between the current branch, your working tree contents, and the new branch is done, and you will be on the new branch.

### `git merge`

The `git merge` command lets you take the independent lines of development created by `git branch` and integrate them into a single branch. It incorporates changes from the named commits (since the time their histories diverged from the current branch) into the current branch. This command is used by `git pull` to incorporate changes from another repository and can be used by hand to merge changes from one branch into another. `git merge` will combine multiple sequences of commits into one unified history. In the most frequent use cases, `git merge` is used to combine two branches.

#### Three Way Merge

Say we have a new branch `feature` that is based off the `master` branch. We now want to merge this feature branch into `master`.

![](https://i.imgur.com/1ABaLsQ.png)

```bash
git merge feature
```

Invoking this command will merge the specified branch feature into the current branch, we'll assume `master`. Git will determine the merge algorithm automatically. It will replay the changes made on the `feature` branch since it diverged from `master` (i.e., `common-base`) until its current commit on top of `master`, and record the result in a new commit along with the names of the two parent commits and a log message from the user describing the changes.

In this case there is not a linear path from the current branch to the target branch, so Git has no choice but to combine them via a **3-way merge**. 3-way merges use a dedicated commit to tie together the two histories. The nomenclature comes from the fact that Git uses three commits to generate the merge commit: the two branch tips and their common ancestor.

![](https://i.imgur.com/V6GXsTc.png)

#### Two Way Merge

A **2-way merge** or **fast-forward** merge can occur when there is a linear path from the current branch tip to the target branch. Instead of "actually" merging the branches, all Git has to do to integrate the histories is move (i.e., "fast forward") the current branch tip up to the target branch tip. This is the most common case especially when invoked from `git pull`: you are tracking an upstream repository, you have committed no local changes, and now you want to update to a newer upstream revision. This effectively combines the histories, since all of the commits reachable from the target branch are now available through the current one.
For example, a fast forward merge of `feature` into `master` using `git merge feature` when on `master` as current branch, would look something like:

![](https://i.imgur.com/GvjzB7N.png)

However, a fast-forward merge is not possible if the branches have diverged. When there is not a linear path to the target branch, Git has no choice but to combine them via a 3-way merge.

```bash
git merge -ff <branch>
git merge --no-ff <branch>
git merge --ff-only <branch>
```

`--ff`: When possible resolve the merge as a fast-forward (only update the branch pointer to match the merged branch; do not create a merge commit). When not possible (when the merged-in history is not a descendant of the current history), create a merge commit. This is the default unless merging an annotated (and possibly signed) tag that is not stored in its natural place in the `refs/tags/` hierarchy, in which case `--no-ff` is assumed.
`--no-ff`: Create a merge commit in all cases, even when the merge could instead be resolved as a fast-forward.
`--ff-only`: Resolve the merge as a fast-forward when possible. When not possible, refuse to merge and exit with a non-zero status.

```bash
git merge --squash
git merge --no-squash
```

Produce the working tree and index state as if a real merge happened (except for the merge information), but do not actually make a commit, move the `HEAD`, or record `$GIT_DIR/MERGE_HEAD` (to cause the next `git commit` command to create a merge commit). This allows you to create a single commit on top of the current branch whose effect is the same as merging another branch (or more in case of an octopus). With `--no-squash` (default behavior) perform the merge and commit the result.

#### Merge Strategies

Git has several different methods to find a base commit, these methods are called "merge strategies". Once Git finds a common base commit it will create a new "merge commit" that combines the changes of the specified merge commits. Technically, a merge commit is a regular commit which just happens to have two parent commits. The merge mechanism (`git merge` and `git pull` commands) allows the backend merge strategies to be chosen with `-s` option. Some strategies can also take their own options, which can be passed by giving `-X <option>` arguments to `git merge` and/or `git pull`. There are many merge strategies in git,  but the most common are the following:

The **recursive** strategy operates on two heads. Recursive is the default merge strategy when pulling or merging one branch. Additionally this can detect and handle merges involving renames, but currently cannot make use of detected copies. This is the default merge strategy when pulling or merging one branch. The **resolve** strategy can only resolve two heads using a 3-way merge algorithm. It tries to carefully detect cris-cross merge ambiguities and is considered generally safe and fast. The **octopus** is the default merge strategy for more than two heads. When more than one branch is passed octopus is automatically engaged. If a merge has conflicts that need manual resolution octopus will refuse the merge attempt. It is primarily used for bundling similar feature branch heads together.

**Explicit merges** are the default merge type. The *explicit* part is that they create a new merge commit. This alters the commit history and explicitly shows where a merge was executed. The merge commit content is also explicit in the fact that it shows which commits were the parents of the merge commit.

An **implicit merge** takes a series of commits from a specified branch head and applies them to the top of a target branch. Whereas explicit merges create a merge commit, implicit merges do not. Implicit merges are triggered by rebase events, or fast forward merges. An implicit merge is an ad-hoc selection of commits from a specified branch. Another type of implicit merge is a squash. A squash can be performed during an interactive rebase. A squash merge will take the commits from a target branch and combine or squash them in to one commit. This commit is then appended to the `HEAD` of the merge base branch. A squash is commonly used to keep a 'clean history' during a merge. The target merge branch can have a verbose history of frequent commits. When squashed and merged the target branches commit history then becomes a singular squashed 'branch commit'.

#### Merge Conflicts

Git can automatically merge commits unless there are changes that conflict in both commit sequences. Conflicts generally arise when two people have changed the same lines in a file, or if one developer deleted a file while another developer was modifying it. In these cases, Git cannot automatically determine what is correct. Conflicts only affect the developer conducting the merge, the rest of the team is unaware of the conflict. Git will mark the file as being conflicted and halt the merging process. It is then the developers' responsibility to resolve the conflict. 

A merge can enter a conflicted state at two separate points: when *starting* and *during* a merge process. A merge will fail to start when Git sees there are changes in either the working directory or staging area of the current project. Git fails to start the merge because these pending changes could be written over by the commits that are being merged in. When this happens, it is not because of conflicts with other developer's, but conflicts with pending local changes. The local state will need to be stabilized using `git stash`, `git checkout`, `git commit` or `git reset`.

A failure *during* a merge indicates a conflict between the current local branch and the branch being merged. This indicates a conflict with another developers code. Git will do its best to merge the files but will leave things for you to resolve manually in the conflicted files. Git will produce some descriptive output letting us know that a conflict has occured. We can gain further insight by running the `git status` command. There are many tools to help resolve merge conflicts. Git has plenty of command line tools to aid in this process.

#### Examples

Let's start by looking at a simple modification for a file (call it *Base*) by two different authors (*Yours* and *Mine*):

![](https://i.imgur.com/ZfYwh9S.png)

Only one developer actually changed line 30, so the conflict can be manually resolved: Just keep "Yours" as the solution, so it will say: `Print("hello");`. This is how 3-way merge helps: It turns a manual conflict into an automatic resolution. Part of the magic here relies on the VCS locating the original version of the file. This original version is better known as the "nearest common ancestor". The VCS then passes the common ancestor and the two contributors to the 3-way merge tool that will use all three to calculate the result.

Now let's chack a more complex case, as shown below:

![](https://i.imgur.com/CkCLuvk.png)

Comparing the two files side by side, we can see that there are three lines with differences. Let's now look at the common ancestor to be able to properly solve the conflicts:

- The conflict on line 30 can be automatically solved and the "yours" (source contributor) will be kept as result because only one contributor modified.
- The conflict on line 70 can also be automatically solved to "mine" (destination contributor) because it is clear now that the line has been added and it wasn't there before.
- The conflict on line 51 needs manual resolution: You need to decide whether you want to keep one of the contributors, the other, or even modify it manually.

## Rewriting History

### `git reflog`

Git keeps track of updates to the tip of branches using a mechanism called **reference log**, or **reflog**. The general us of the command is:

```
git reflog <subcommand> <options>
```

The command takes various subcommands, and different options depending on the subcommand.

```bash
git reflog
```

The above command is essentially a shortcut which is equivalent to `git reflog show HEAD`.

```bash
git reflog show [-a | --all]
```

This gets the complete reflog of all refs.

```bash
git reflog show <branchname>
```

Show a reflog only for branch `<branchname>`.

```bash
git reflog stash
```

Output a reflog for the Git stash.

Git never really loses anything, even when performing history rewriting operations like rebasing or commit amending. `git reflog` can thus be used to restore lost commits e.g. when using `git reset` or rebasing.

### `git rebase`

In Git, there are two main ways to integrate changes from one branch into another: `git merge` and `git rebase`. Merge is always a forward moving change record. Alternatively, rebase has powerful history rewriting features.

Rebasing is the process of moving or combining a sequence of commits to a new base commit. From a content perspective, rebasing is changing the base of your branch from one commit to another making it appear as if you'd created your branch from a different commit. Internally, Git accomplishes this by creating new commits and applying them to the specified base. Note that even though the branch looks the same, it's composed of entirely new commits. 

The primary reason for rebasing is to maintain a linear project history. For example, consider a situation where the `master` branch has progressed since you started working on a `feature` branch. You want to get the latest updates to the `master` branch in your `feature` branch, but you want to keep your branch's history clean so it appears as if you've been working off the latest `master` branch. This gives the later benefit of a clean merge of your `feature` branch back into the `master` branch.

`git rebase` in standard mode will automatically take the commits in your current working branch and apply them to the head of the passed branch.

```bash
git rebase <base>
```

This automatically rebases the current branch onto `<base>`, which can be any kind of commit reference (for example an ID, a branch name, a tag, or a relative reference to `HEAD`). The general process can be visualized as:

![](https://i.imgur.com/lbmXTJb.png)

In this case, with `feature` as the current branch, running `git rebase master` will rebase the `feature` branch on the `master` branch.

**Note:** You should never rebase commits once they've been pushed to a public repository. The rebase would replace the old commits with new ones and it would look like that part of your project history abruptly vanished. This is also true about amended commits. Amended commits are actually entirely new commits and the previous commit will no longer be on your current branch. This has the same consequences as resetting a public snapshot. Avoid amending a commit that other developers have based their work on. This is a confusing situation for developers to be in and it's complicated to recover from.

The general form of the `git rebase` is:

```bash
git rebase [-i | --interactive] [options] [--exec <cmd>] [--onto <newbase> | --keep-base] [<upstream> [<branch>]]
```

#### Common Options

- `--onto <newbase>`: Starting point at which to create the new commits. If the `--onto` option is not specified, the starting point is `<upstream>`. May be any valid commit, and not just an existing branch name. As a special case, you may use `A...B` as a shortcut for the merge base of A and B if there is exactly one merge base. You can leave out at most one of `A` and `B`, in which case it defaults to `HEAD`.
- `--keep-base`: Set the starting point at which to create the new commits to the merge base of `<upstream>` `<branch>`. Running `git rebase --keep-base <upstream> <branch>` is equivalent to running `git rebase --onto <upstream>...​ <upstream>`. This option is useful in the case where one is developing a feature on top of an upstream branch. While the feature is being worked on, the upstream branch may advance and it may not be the best idea to keep rebasing on top of the upstream but to keep the base commit as-is.
- `<upstream>`: Upstream branch to compare against. May be any valid commit, not just an existing branch name. Defaults to the configured upstream for the current branch.
- `<branch>`: Working branch; defaults to `HEAD`.

If `<branch>` is specified, `git rebase` will perform an automatic `git switch <branch>` before doing anything else. Otherwise it remains on the current branch. Assume the following history exists and the current branch is `topic`:

```
          A---B---C topic
         /
    D---E---F---G master
```

From this point, the result of either of the following commands:

```bash
git rebase master
git rebase master topic
```

would be:

```
                  A'--B'--C' topic
                 /
    D---E---F---G master
```

**Note**: The latter form is just a short-hand of `git checkout topic` followed by `git rebase master`. When rebase exits topic will remain the checked-out branch.

Here is how you would transplant a topic branch based on one branch to another, to pretend that you forked the topic branch from the latter branch, using `rebase --onto`. First let's assume your `topic` is based on branch `next`. For example, a feature developed in topic depends on some functionality which is found in next.

```
    o---o---o---o---o  master
         \
          o---o---o---o---o  next
                           \
                            o---o---o  topic
```

We want to make `topic` forked from branch `master`; for example, because the functionality on which topic depends was merged into the more stable `master` branch. We want our tree to look like this:

```
    o---o---o---o---o  master
        |            \
        |             o'--o'--o'  topic
         \
          o---o---o---o---o  next
```

We can get this using the following command:

```bash
git rebase --onto master next topic
```

Another example of `--onto` option is to rebase part of a branch. If we have the following situation:

```
                            H---I---J topicB
                           /
                  E---F---G  topicA
                 /
    A---B---C---D  master
```

then the command:

```bash
git rebase --onto master topicA topicB
```

would result in:

```
                 H'--I'--J'  topicB
                /
                | E---F---G  topicA
                |/
    A---B---C---D  master
```

This is useful when topicB does not depend on `topicA`.

A range of commits could also be removed with rebase. If we have the following situation:

```
    E---F---G---H---I---J  topicA
```
then the command

```bash
git rebase --onto topicA~5 topicA~3 topicA
```

would result in the removal of commits `F` and `G`:

```
    E---H'---I'---J'  topicA
```

This is useful if `F` and `G` were flawed in some way, or should not be part of `topicA`. Note that the argument to `--onto` and the `<upstream>` parameter can be any valid commit-ish.

Running `git rebase`with the `-i` flag begins an *interactive* rebasing session. Instead of blindly moving all of the commits to the new base, interactive rebasing gives you the opportunity to alter individual commits in the process. This lets you clean up history by removing, splitting, and altering an existing series of commits.

```bash
git rebase -i <base>
```

This rebases the current branch onto `<base>` but uses an interactive rebasing session. This opens an editor where you can enter commands (described below) for each commit to be rebased. These commands determine how individual commits will be transferred to the new base. You can also reorder the commit listing to change the order of the commits themselves. Once you've specified commands for each commit in the rebase, Git will begin playing back commits applying the rebase commands.

In case of conflict, `git rebase` will stop at the first problematic commit and leave conflict markers in the tree. After resolving the conflict manually and updating the index with the desired resolution, you can continue the rebasing process with:

```bash
git rebase --continue
```

Alternatively, you can undo the `git rebase` with:

```bash
git rebase --abort
```

**Note**: Use `git rebase` with care, as it is a history rewriting command. The real danger of `git rebase` cases arise when executing history rewriting interactive rebases and force pushing the results to a remote branch that's shared by other users. This is a pattern that should be avoided as it has the capability to overwrite other remote users' work when they pull.

## Collaborating

### `git remote`

Remote repositories are versions of your project that are hosted on the Internet or network somewhere. You can have several of them, each of which generally is either read-only or read/write for you. Collaborating with others involves managing these remote repositories and pushing and pulling data to and from them when you need to share work. Managing remote repositories includes knowing how to add remote repositories, remove remotes that are no longer valid, manage various remote branches and define them as being tracked or not, and more.

The `git remote` command is one piece of the broader system which is responsible for syncing changes. Records registered through the `git remote` command are used in conjunction with the `git fetch`, `git push`, and `git pull` commands. The `git remote` command lets you create, view, and delete connections to other repositories. Remote connections are more like bookmarks rather than direct links into other repositories. Instead of providing real-time access to another repository, they serve as convenient names that can be used to reference a not-so-convenient URL.

```bash
git remote [-v | verbose]
```

Lists the remote connections you have to other repositories. If `-v` option is included, be a little more verbose and show remote URL after name (this must be placed between `remote` and `subcommand`).

```bash
git remote show <name>
```

Gives some information about the remote `<name>`.

The `git remote` command is essentially an interface for managing a list of remote entries that are stored in the repository's `./.git/config` file. The following commands will modify the repo's `/.git/config` file. The result of the following commands can also be achieved by directly editing the `./.git/config` file with a text editor.

```bash
git remote add [-t <branch>] [-m <master>] [-f] [--[no-]tags] [--mirror=<fetch|push>] <name> <url>
```

Create a new connection to a remote repository. After adding a remote, you'll be able to use `<name>` as a convenient shortcut for `<url>` in other Git commands.

- `-f`: `git fetch <name>` is run immediately after the remote information is set up.
- `--tags`: `git fetch <name>` imports every tag from the remote repository.
- `--no-tags`: `git fetch <name>` does not import tags from the remote repository. By default, only tags on fetched branches are imported (see [`git fetch`](#git-fetch)).
- `-t <branch>`: Instead of the default glob refspec for the remote to track all branches under the `refs/remotes/<name>/` namespace, a refspec to track only `<branch>` is created. You can give more than one `-t <branch>` to track multiple branches without grabbing all branches.
- `-m <master>`: A symbolic-ref `refs/remotes/<name>/HEAD` is set up to point at remote's `<master>` branch. See also the `set-head` command.

```bash
git remote rm name
git remote remove name
```

Remove the remote named `<name>`. All remote-tracking branches and configuration settings for the remote are removed.

```bash
git remote rename <old-name> <new-name>
```

Rename a remote connection from `<old-name>` to `<new-name>`.

### `git fetch`

The `git fetch` command downloads branches and/or tags (collectively, "refs") from one or more other repositories, along with the objects necessary to complete their histories. Fetching is what you do when you want to see what everybody else has been working on. It lets you see how the central history has progressed, but it doesn't force you to actually merge the changes into your repository. Git isolates fetched content as a from existing local content, it has absolutely no effect on your local development work. Fetched content has to be explicitly checked out using the `git checkout` command. This makes fetching a safe way to review commits before integrating them with your local repository.

When downloading content from a remote repo, `git pull` and `git fetch` commands are available to accomplish the task. You can consider `git fetch` the "safe" version of the two commands. It will download the remote content but not update your local repo's working state, leaving your current work intact. `git pull` is the more aggressive alternative, it will download the remote content for the active local branch and immediately execute `git merge` to create a merge commit for the new remote content. If you have pending changes in progress this will cause conflicts and kickoff the merge conflict resolution flow.

You can inspect remote branches with the usual `git checkout` and `git log` commands. If you approve the changes a remote branch contains, you can merge it into a local branch with a normal `git merge`. So, synchronizing your local repository with a remote repository is actually a two-step process: fetch, then merge. The `git pull` command is a convenient shortcut for this process.

The general form of the command is:

```bash
git fetch [<options>] [<repository> [<refspec>...]]
git fetch [<options>] <group>
```

`git fetch` can fetch from either a single named repository or URL, or from several repositories at once if `<group>` is given and there is a remotes. `<group>` entry in the configuration file. When no remote is specified, by default the `origin` remote will be used, unless there's an upstream branch configured for the current branch. The names of refs that are fetched, together with the object names they point at, are written to `.git/FETCH_HEAD`.

#### Common Options

- `-v, --verbose`: Be more verbose.
- `-q, --quiet`: Be more quiet.
- `--all`: Fetch from all remotes.
- `--set-upstream`: Set upstream for `git pull/fetch`.
- `-f, --force`: Force overwrite of local reference.
- `-m, --multiple`: Fetch from multiple remotes.
- `-t, --tags`: Fetch all tags and associated objects.
- `-n, --no-tags`: Do not fetch all tags.
- `--dry-run`: Dry run.

```bash
git fetch <remote>
```

Fetch all of the branches from the repository. This also downloads all of the required commits and files from the other repository.

```bash
git fetch <remote> <branch>
```

Same as the above command, but only fetch the specified branch.

```bash
git fetch --all
```

Fetches all registered remotes and their branches.

### `git pull`

The `git pull` command is used to fetch and download content from a remote repository and immediately update the local repository to match that content. Merging remote upstream changes into your local repository is a common task in Git-based collaboration work flows. In the first stage of operation `git pull` will execute a `git fetch` scoped to the local branch that `HEAD` is pointed at. Once the content is downloaded, `git pull` will enter a merge workflow. A new merge commit will be-created and `HEAD` updated to point at the new commit. In its default mode, `git pull` is shorthand for `git fetch` followed by `git merge FETCH_HEAD`. More precisely, `git pull` runs `git fetch` with the given parameters and calls `git merge` to merge the retrieved branch heads into the current branch. With `--rebase`, it runs `git rebase` instead of `git merge`.

The `git fetch` command can be confused with `git pull`. They are both used to download remote content. An important safety distinction can me made between git pull and get fetch. `git fetch` can be considered the "safe" option whereas, `git pull` can be considered unsafe. `git fetch` will download the remote content and not alter the state of the local repository. Alternatively, `git pull` will download remote content and immediately attempt to change the local state to match that content. This may unintentionally cause the local repository to get in a conflicted state.

The general form of the command is:

```bash
git pull [<options>] [<repository> [<refspec>...]]
```

`<repository>` should be the name of a remote repository as passed to `git fetch`. `<refspec>` can name an arbitrary remote ref (for example, the name of a tag) or even a collection of refs with corresponding remote-tracking branches (e.g., `refs/heads/*:refs/remotes/origin/*`), but usually it is the name of a branch in the remote repository.

Default values for `<repository>` and `<branch>` are read from the "remote" and "merge" configuration for the current branch as set by `git branch --track`.

![](https://i.imgur.com/X0EfZ0v.png)

The above diagram explains each step of the pulling process. You start out thinking your repository is synchronized, but then `git fetch` reveals that origin's version of `master` has progressed since you last checked it. Then `git merge` immediately integrates the remote `master` into the local one.

![](https://i.imgur.com/xTjDNTb.png)

In this scenario, `git pull` will download all the changes from the point where the local and master diverged. `git pull` will fetch the diverged remote commits which are `A-B-C`. The pull process will then create a new local merge commit containing the content of the new diverged remote commits. In the above diagram, we can see the new commit `H`. This commit is a new merge commit that contains the contents of remote `A-B-C` commits and has a combined log message.

This example is one of a few `git pull` merging strategies. A `--rebase` option can be passed to `git pull` to use a rebase merging strategy instead of a merge commit. Assume that we are at a starting point of our first diagram, and we have executed `git pull --rebase`. In the third diagram, we can now see that a rebase pull does not create the new `H` commit. Instead, the rebase has copied the remote commits `A-B-C` and appended them to the local `origin/master` commit history.

```bash
git pull <remote>
```

This is the default invocation, which fetches the specified remote's copy of the current branch and immediately merge it into the local copy. This is the same as `git fetch <remote>` followed by `git merge origin/<current-branch>`.

#### Common Options

- `--commit`: Perform the merge and commit the result.
- `--no-commit`: Perform the merge and stop just before creating a merge commit, to give the user a chance to inspect and further tweak the merge result before committing.
- `-e, --edit`: Invoke an editor before committing successful mechanical merge to further edit the auto-generated merge message, so that the user can explain and justify the merge.
- `--no-edit`: This option can be used to accept the auto-generated message (generally discouraged).
- `--ff`: When possible resolve the merge as a fast-forward (only update the branch pointer to match the merged branch; do not create a merge commit). When not possible (when the merged-in history is not a descendant of the current history), create a merge commit.
- `--no-ff`: Create a merge commit in all cases, even when the merge could instead be resolved as a fast-forward.
- `-r, --rebase`: Instead of using `git merge` to integrate the remote branch with the local one, use `git rebase` to rebase the current branch on top of the upstream branch after fetching.

### `git push`

The `git push` command is used to upload local repository content to a remote repository. It's the counterpart to `git fetch`, but whereas fetching imports commits to local branches, pushing exports commits to remote branches. Remote branches are configured using the `git remote` command. Pushing has the potential to overwrite changes, so caution should be taken when pushing.

`git push` is most commonly used to publish an upload local changes to a central repository. After a local repository has been modified a push is executed to share the modifications with remote team members.

![](https://i.imgur.com/XGtofYW.png)

The above diagram shows what happens when your local `master` has progressed past the central repository's `master` and you publish changes by running `git push origin master`. Notice how `git push` is essentially the same as running `git merge master` from inside the remote repository.

Git prevents you from overwriting the central repository's history by refusing push requests when they result in a non-fast-forward merge. So, if the remote history has diverged from your history, you need to pull the remote branch and merge it into your local one, then try pushing again.

The `--force` flag (see also below) overrides this behavior and makes the remote repository's branch match your local one, deleting any upstream changes that may have occurred since you last pulled. The only time you should ever need to force push is when you realize that the commits you just shared were not quite right and you fixed them with a `git commit --amend` or an interactive rebase. However, you must be absolutely certain that none of your teammates have pulled those commits before using the `--force` option.

```bash
git push [<options>] [<repository> [<refspec>...]]
```

When the command line does not specify where to push with the `<repository>` argument, `branch.*.remote` configuration for the current branch is consulted to determine where to push. If the configuration is missing, it defaults to `origin`.

When the command line does not specify what to push with `<refspec>...` arguments or `--all`, `--mirror`, `--tags` options, the command finds the default `<refspec>` by consulting `remote.*.push` configuration, and if it is not found, honors `push.default` configuration to decide what to push.

```bash
git push <remote> <branch>
```

Push the specified branch to `<remote>`, along with all of the necessary commits and internal objects. This creates a local branch in the destination repository. To prevent you from overwriting commits, Git won't let you push when it results in a non-fast-forward merge in the destination repository.

```bash
git push <remote> [-f | --force]
```

Same as the above command, but force the push even if it results in a non-fast-forward merge. Do not use the `--force` flag unless you’re absolutely sure you know what you're doing.

```bash
git push <remote> --all
```

Push all of your local branches to the specified remote.

```bash
git push <remote> --tags
```

Tags are not automatically pushed when you push a branch or use the `--all` option. The `--tags` flag sends all of your local tags to the remote repository.

Sometimes branches need to be cleaned up for book keeping or organizational purposes. The fully delete a branch, it must be deleted locally and also remotely.

```bash
git branch -D branch_name
git push origin :branch_name
```

The above will delete the remote branch named `branch_name` passing a branch name prefixed with a colon to `git push` will delete the remote branch.

#### Refspecs

A refspec maps a branch in the local repository to a branch in a remote repository. This makes it possible to manage remote branches using local Git commands and to configure some advanced `git push` and `git fetch` behavior.

A refspec is specified as `[+]<src>:<dst>`. The `<src>` parameter is the source branch in the local repository, and the `<dst>` parameter is the destination branch in the remote repository. The optional `+` sign is for forcing the remote repository to perform a non-fast-forward update.

Refspecs can be used with the `git push` command to give a different name to the remote branch. For example, the following command pushes the `master` branch to the `origin` remote repo like an ordinary `git push`, but it uses `qa-master` as the name for the branch in the origin repo. This is useful for QA teams that need to push their own branches to a remote repo.

```bash
git push origin master:refs/heads/qa-master
```

You can also use refspecs for deleting remote branches. This is a common situation for feature-branch workflows that push the feature branches to a remote repo (e.g. for backup purposes). The remote feature branches still reside in the remote repo after they are deleted from the local repo, so you get a build-up of dead feature branches as your project progresses. You can delete them by pushing a refspec that has an empty `<src>` parameter. Note that as of Git v1.7.0 you can use the `--delete` flag instead of the previous method. Both commands below have the same effect.

```bash
git push origin :some-feature
git push origin --delete some-feature
```

By adding a few lines to the Git configuration file, you can use refspecs to alter the behavior of `git fetch`. By default, `git fetch` fetches all of the branches in the remote repository. The reason for this is the following section of the `.git/config` file:

```bash
[remote "origin"]
url = https://git@github.com:mary/example-repo.git
fetch = +refs/heads/*:refs/remotes/origin/*

```

The fetch line tells git fetch to download all of the branches from the `origin` repo. But, some workflows don't need all of them. For example, many continuous integration workflows only care about the master branch. To fetch only the master branch, change the fetch line to match the following:

```bash
[remote "origin"]
url = https://git@github.com:mary/example-repo.git
fetch = +refs/heads/master:refs/remotes/origin/master
```

You can also configure `git push` in a similar manner. For instance, if you want to always push the master branch to `qa-master` in the origin remote (as we did above), you would change the config file to:

```bash
[remote "origin"]
url = https://git@github.com:mary/example-repo.git
fetch = +refs/heads/master:refs/remotes/origin/master
push = refs/heads/master:refs/heads/qa-master
```

Refspecs give you complete control over how various Git commands transfer branches between repositories. They let you rename and delete branches from your local repository, fetch/push to branches with different names, and configure `git push` and `git fetch` to work with only the branches that you want.

## Gitflow Workflow

A Git Workflow is a recipe or recommendation for how to use Git to accomplish work in a consistent and productive manner. Git workflows encourage users to leverage Git effectively and consistently. Git offers a lot of flexibility in how users manage changes. Given Git's focus on flexibility, there is no standardized process on how to interact with Git. When working with a team on a Git managed project, it’s important to make sure the team is all in agreement on how the flow of changes will be applied. To ensure the team is on the same page, an agreed upon Git workflow should be developed or selected.

The Gitflow Workflow defines a strict branching model designed around the project release. This provides a robust framework for managing larger projects.

### Develop and Master Branches

Instead of a single `master` branch, this workflow uses two branches to record the history of the project. The `master` branch stores the official release history, and the `develop` branch serves as an integration branch for features. It's also convenient to tag all commits in the `master` branch with a version number.

![](https://i.imgur.com/CH3iBGr.png)

The first step is to complement the default `master` with a `develop` branch. A simple way to do this is for one developer to create an empty `develop` branch locally and push it to the server:

```bash
git branch develop
git push -u origin develop
```

This branch will contain the complete history of the project, whereas `master` will contain an abridged version. Other developers should now clone the central repository and create a tracking branch for `develop`. When using the `git-flow` extension library, executing `git flow init` on an existing repo will create the `develop` branch.

### Feature Branches

Each new feature should reside in its own branch, which can be pushed to the central repository for backup/collaboration. But, instead of branching off of `master`, `feature` branches use `develop` as their parent branch. When a feature is complete, it gets merged back into develop. Features should never interact directly with `master`.

![](https://i.imgur.com/f3vF98y.png)

Note that `feature` branches combined with the `develop` branch is, for all intents and purposes, the Feature Branch Workflow. But, the Gitflow Workflow doesn't stop there. `feature` branches are generally created off to the latest `develop` branch.

#### Creating a Feature Branch

Without the `git-flow` extension:

```bash
git checkout develop
git checkout -b feature_branch
```

When using the `git-flow` extension:

```bash
git flow feature start feature_branch
```

Continue your work and use Git like you normally would.

#### Finishing a Feature Branch

When you're done with the development work on the feature, the next step is to merge the `feature_branch` into `develop`.

Without the `git-flow` extension:

```
git checkout develop
git merge feature_branch
```

Using the `git-flow` extension:

```
git flow feature finish feature_branch
```

### Release Branches

![](https://i.imgur.com/xm7TsYO.png)

Once `develop` has acquired enough features for a release (or a predetermined release date is approaching), you fork a `release` branch off of `develop`. Creating this branch starts the next release cycle, so no new features can be added after this point-only bug fixes, documentation generation, and other release-oriented tasks should go in this branch. Once it's ready to ship, the `release` branch gets merged into `master` and tagged with a version number. In addition, it should be merged back into `develop`, which may have progressed since the release was initiated.

Using a dedicated branch to prepare releases makes it possible for one team to polish the current release while another team continues working on features for the next release. It also creates well-defined phases of development (e.g., it's easy to say, "This week we're preparing for version 4.0" and to actually see it in the structure of the repository).

Making `release` branches is another straightforward branching operation. Like `feature` branches, `release` branches are based on the `develop` branch. A new `release` branch can be created using the following methods.

Without the `git-flow` extension:

```bash
git checkout develop
git checkout -b release/0.1.0
```

When using the `git-flow` extension:

```bash
$ git flow release start 0.1.0
Switched to a new branch 'release/0.1.0'
```

Once the release is ready to ship, it will get merged it into `master` and `develop`, then the `release` branch will be deleted. It's important to merge back into `develop` because critical updates may have been added to the `release` branch and they need to be accessible to new features. If your organization stresses code review, this would be an ideal place for a pull request.

To finish a `release` branch, use the following methods:

Without the `git-flow` extension:

```bash
git checkout master
git merge release/0.1.0
```

Or with the `git-flow` extension:

```bash
git flow release finish '0.1.0'
```

### Hotfix Branches

![](https://i.imgur.com/XyYJVK2.png)

Maintenance or `hotfix` branches are used to quickly patch production releases. `hotfix` branches are a lot like `release` branches and `feature` branches except they're based on `master` instead of `develop`. This is the only branch that should fork directly off of `master`. As soon as the fix is complete, it should be merged into both `master` and `develop` (or the current `release` branch), and `master` should be tagged with an updated version number.

Having a dedicated line of development for bug fixes lets your team address issues without interrupting the rest of the workflow or waiting for the next release cycle. You can think of maintenance branches as ad hoc `release` branches that work directly with `master`. A `hotfix` branch can be created using the following methods:

Without the `git-flow` extension:

```bash
git checkout master
git checkout -b hotfix_branch
```

When using the `git-flow` extension:

```bash
$ git flow hotfix start hotfix_branch
```

Similar to finishing a `release` branch, a `hotfix` branch gets merged into both `master` and `develop`.

```bash
git checkout master
git merge hotfix_branch
git checkout develop
git merge hotfix_branch
git branch -D hotfix_branch
```

```bash
$ git flow hotfix finish hotfix_branch
```

### Gitflow Summary

The overall flow of Gitflow is:
 
1. A `develop` branch is created from `master`.
2. A `release` branch is created from `develop`.
3. `feature` branches are created from `develop`.
4. When a `feature` is complete it is merged into the `develop` branch.
5. When the `release` branch is done it is merged into `develop` and `master`.
6. If an issue in `master` is detected, a `hotfix` branch is created from `master`.
7. Once the `hotfix` is complete, it is merged to both `develop` and `master`.

## Git Hooks

Like many other Version Control Systems, Git has a way to fire off custom scripts when certain important actions occur. There are two groups of these hooks: client-side (local) and server-side. Client-side hooks are triggered by operations such as committing and merging, while server-side hooks run on network operations such as receiving pushed commits, and they are only executed in response to actions in that repository. You can use these hooks for all sorts of reasons.

### Installing a Hook

The hooks are all stored in the hooks subdirectory of the Git directory. In most projects, that's `.git/hooks`. When you initialize a new repository with `git init`, Git populates the hooks directory with a bunch of example scripts, many of which are useful by themselves; but they also document the input values of each script. All the examples are written as shell scripts, with some Perl thrown in, but any properly named executable scripts will work fine - you can write them in Ruby or Python or whatever language you are familiar with. If you want to use the bundled hook scripts, you'll have to rename them; their file names all end with `.sample`.

To enable a hook script, put a file in the hooks subdirectory of your `.git` directory that is named appropriately (without any extension) and is executable. From that point forward, it should be called. We' ll cover most of the major hook filenames here.

### Client Side Hooks

Client side (local) hooks affect only the repository in which they reside. As you read through this section, remember that each developer can alter their own local hooks, so you can't use them as a way to enforce a commit policy.

These are 6 of the most useful local hooks:

- `pre-commit`
- `prepare-commit-msg`
- `commit-msg`
- `post-commit`
- `post-checkout`
- `pre-rebase`

The first 4 hooks let you plug into the entire commit life cycle, and the final 2 let you perform some extra actions or safety checks for the `git checkout` and `git rebase` commands, respectively. All of the pre-hooks let you alter the action that's about to take place, while the post-hooks are used only for notifications.

### Server Side Hooks

Server-side hooks work just like local ones, except they reside in server-side repositories (e.g., a central repository, or a developer's public repository). When attached to the official repository, some of these can serve as a way to enforce policy by rejecting certain commits.

These are 3 common server-side hooks:

- `pre-receive`
- `update`
- `post-receive`

All of these hooks let you react to different stages of the `git push` process.

The output from server-side hooks are piped to the client's console, so it's very easy to send messages back to the developer. But, you should also keep in mind that these scripts don't return control of the terminal until they finish executing, so you should be careful about performing long-running operations.

### Git Hooks Summary

Git hooks can be used to alter internal behavior and receive notifications when certain events occur in a repository. Hooks are ordinary scripts that reside in the `.git/hooks` repository, which makes them very easy to install and customize.

Some of the most common local and server-side hooks let us plug in to the entire development life cycle. We now know how to perform customizable actions at every stage in the commit creation process, as well as the `git push` process. With a little bit of scripting knowledge, this lets you do virtually anything you can imagine with a Git repository.

## References

<a id="1">[1]</a> [S. Chacon - Git Internals](https://github.com/pluralsight/git-internals-pdf) (2008)

<a id="2">[2]</a> [S. Chacon - The Git Community Book](https://shafiul.github.io/gitbook)

<a id="3">[3]</a> [S. Chacon & B. Straub - Pro Git](https://git-scm.com/book/en/v2)

<a id="4">[4]</a> [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials)

<a id="5">[5]</a> [Git Official Documentation](https://git-scm.com/docs)

<a id="6">[6]</a> [StackOverflow - What does tree-ish mean in Git?](https://stackoverflow.com/questions/4044368/what-does-tree-ish-mean-in-git)

<a id="7">[7]</a> [Dr. Dobbs - Three-Way Merging: A Look Under the Hood](https://www.drdobbs.com/tools/three-way-merging-a-look-under-the-hood/240164902)

