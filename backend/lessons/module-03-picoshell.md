# Module 03: Understanding Shells - The Foundation of AI Agent Execution

## Why This Matters for AI Agents

Every time an AI agent runs code, uses a tool, or executes a command, it's using **shell concepts** under the hood. Understanding how shells work isn't just academic—it's fundamental to understanding how AI systems interact with computers.

**Key Insight:** When Claude (or any AI agent) runs a bash command, compiles your code, or executes a test, it's using `exec()` or `execvp()` system calls—the exact same primitives you'll implement in the picoshell exam.

---

## What is a Shell?

A shell is a **command interpreter** that:
1. Reads commands from the user
2. Parses the command into programs and arguments
3. Creates new processes to run those programs
4. Connects processes together (pipes, redirection)
5. Waits for processes to complete

Examples: bash, zsh, fish, sh

---

## The Two Fundamental System Calls

### 1. `fork()` - Create a New Process

```
fork() creates a copy of the current process

Parent Process                Child Process
     |                              |
  fork() -----------------------> fork()
     |                              |
  (returns child PID)          (returns 0)
     |                              |
  continues...                 continues...
```

**What happens:**
- Creates an identical copy of the calling process
- Both processes continue from the same point
- Parent gets child's PID, child gets 0
- Both have separate memory spaces

### 2. `execvp()` - Replace Process with New Program

```
execvp(program, args) replaces the current process

Before exec:                After exec:
+-----------+              +-----------+
| Your Code |  execvp()    | New       |
| Running   |  -------->   | Program   |
|           |              | Running   |
+-----------+              +-----------+

Original process is GONE, replaced entirely
```

**What happens:**
- Current process code is replaced with new program
- New program starts executing
- Process ID (PID) stays the same
- If exec succeeds, this function NEVER returns!

---

## How Shells Use Fork + Exec

Every time you run a command in a shell, this happens:

```
1. Shell calls fork()
   → Creates child process (copy of shell)

2. Child process calls execvp()
   → Replaces itself with the command you typed

3. Parent shell calls wait()
   → Waits for child to finish

4. Child finishes, parent resumes
   → Shell shows prompt again
```

**Example: Running `ls`**

```
bash$ ls              ← You type this

[bash process]
    |
    fork()  ─────→  [child: copy of bash]
    |                      |
    |                  execvp("ls", args)
    |                      |
    |                  [child becomes ls process]
    |                      |
    wait()  ←─────────  [ls runs and exits]
    |
[bash shows prompt again]
```

---

## Pipes: Connecting Processes Together

A **pipe** connects the output of one program to the input of another.

```bash
echo "hello" | cat
```

**What happens:**
1. Create a pipe (two file descriptors: read end, write end)
2. Fork two child processes (one for `echo`, one for `cat`)
3. Connect `echo`'s stdout to pipe write end
4. Connect `cat`'s stdin to pipe read end
5. Both programs run simultaneously

**Visualization:**

```
[echo process]  ─────>  PIPE  ─────>  [cat process]
   stdout                              stdin
```

**System calls involved:**
- `pipe()` - Create the pipe
- `dup2()` - Duplicate file descriptors to redirect stdin/stdout
- `fork()` - Create child processes
- `execvp()` - Replace children with echo and cat

---

## Why AI Agents Need This

### Claude Code's Tool Execution

When you see this in Claude Code:

```
🔧 Running: pytest tests/
```

Behind the scenes:
1. Claude calls `fork()` to create child process
2. Child calls `execvp("pytest", ["pytest", "tests/"])`
3. Claude's parent process waits for result
4. Captures stdout/stderr to show you

### Code Compilation and Execution

When grading your picoshell submission:

```python
# Backend grading system does this:
subprocess.run(['gcc', 'picoshell.c', '-o', 'picoshell'])  # Compilation
subprocess.run(['./picoshell', 'echo', 'hello'])           # Execution
```

**Under the hood:**
- `subprocess.run()` uses fork() + exec()
- Same primitives you're implementing!

### Multi-Agent Systems

When AI agents collaborate:
- Each agent might run in separate process
- Communication happens via pipes or IPC
- Process management uses fork/exec patterns

---

## The Picoshell Challenge

You'll implement a **simplified shell** that can:

1. Execute single commands: `echo hello`
2. Handle pipes: `echo hello | cat`
3. Support multiple pipes: `echo hello | cat | cat`

**Required System Calls:**
- `fork()` - Create child processes
- `pipe()` - Create pipes for inter-process communication
- `dup2()` - Redirect stdin/stdout to pipes
- `execvp()` - Execute programs
- `wait()` or `waitpid()` - Wait for children to finish

---

## Practice Exercises

### Exercise 1: Simple Fork

**Goal:** Understand fork() behavior

Write a program that:
1. Prints "Parent: Before fork"
2. Calls fork()
3. Parent prints "Parent: After fork, child PID = X"
4. Child prints "Child: After fork, my PID = Y"

**Expected output:**
```
Parent: Before fork
Parent: After fork, child PID = 1234
Child: After fork, my PID = 1234
```

**Languages:** Try this in C, Python, and TypeScript

### Exercise 2: Fork + Exec

**Goal:** Run a command from your program

Write a program that:
1. Forks a child process
2. Child calls `exec()` to run `/bin/ls`
3. Parent waits for child to finish
4. Parent prints "Child finished"

**Expected behavior:**
```
[ls output shows files]
Child finished
```

### Exercise 3: Simple Pipe

**Goal:** Connect two processes with a pipe

Write a program that simulates: `echo hello | cat`

1. Create a pipe
2. Fork two children
3. First child: writes "hello\n" to pipe, closes read end
4. Second child: reads from pipe, prints to stdout
5. Parent waits for both children

**Expected output:**
```
hello
```

### Exercise 4: Command with Arguments

**Goal:** Execute a program with arguments

Write a program that executes: `/bin/echo Hello World`

Must use `execvp()` with proper argument array.

---

## Implementation Tips

### C Implementation Tips

```c
// Fork pattern
pid_t pid = fork();
if (pid == 0) {
    // Child process
    // ... do child work ...
    exit(0);  // Don't forget to exit!
} else if (pid > 0) {
    // Parent process
    waitpid(pid, NULL, 0);
}

// Exec pattern
char *args[] = {"ls", "-l", NULL};  // Must be NULL-terminated!
execvp("ls", args);
// If we get here, exec failed
perror("execvp failed");
exit(1);

// Pipe pattern
int pipefd[2];
pipe(pipefd);  // pipefd[0] = read end, pipefd[1] = write end
```

### Python Implementation Tips

```python
import os
import sys

# Fork
pid = os.fork()
if pid == 0:
    # Child
    # ... do work ...
    sys.exit(0)
else:
    # Parent
    os.waitpid(pid, 0)

# Exec (replaces current process!)
os.execvp('ls', ['ls', '-l'])
# Code after exec never runs

# Pipe
r, w = os.pipe()
# r = read end, w = write end
```

### TypeScript/Node.js Implementation Tips

```typescript
import { spawn, fork } from 'child_process';

// Spawn external program
const child = spawn('ls', ['-l']);
child.stdout.on('data', (data) => {
    console.log(data.toString());
});

// For pipes, connect stdin/stdout
```

---

## Exam Preparation

### What You'll Build

A program named `picoshell` that:
- Takes command-line arguments
- Executes commands
- Supports pipe operator `|`
- Example: `./picoshell echo hello | cat`

### Test Cases (Examples)

```bash
# Test 1: Simple command
./picoshell echo hello
# Expected: hello\n

# Test 2: Single pipe
./picoshell echo hello | cat
# Expected: hello\n

# Test 3: Multiple pipes
./picoshell echo "hello world" | cat | cat
# Expected: hello world\n
```

### Grading Criteria

- **100% pass required**: ALL tests must pass
- **Exact output match**: No extra spaces, newlines, or characters
- **Timeout**: Each test has 5-second limit
- **Languages**: Implement in C, Python, OR TypeScript (your choice)

### File Requirements

```
~/exam/picoshell.c       # For C implementation
~/exam/picoshell.py      # For Python implementation
~/exam/picoshell.ts      # For TypeScript implementation
```

### Submission

```bash
# 1. Create your implementation
vim ~/exam/picoshell.c

# 2. Submit for grading
lms exam submit picoshell --lang c

# 3. Check status
lms exam status picoshell

# 4. View results
lms exam results picoshell
```

---

## Resources for Deep Dive

### System Calls Documentation
- `man 2 fork`
- `man 2 execve`
- `man 2 pipe`
- `man 2 dup2`
- `man 2 wait`

### Recommended Reading
- "Advanced Programming in the UNIX Environment" (Stevens & Rago)
- Linux man pages for system calls
- Your operating system's process management documentation

### Key Concepts to Master
1. Process lifecycle (creation, execution, termination)
2. File descriptor manipulation
3. Inter-process communication (pipes)
4. Process synchronization (wait/waitpid)
5. Error handling (always check return values!)

---

## Next Steps

1. **Practice** the exercises above in all three languages
2. **Experiment** with fork, exec, and pipes
3. **Read** the man pages for system calls
4. **Start the exam** when you're ready: `lms exam start picoshell`
5. **Work in ~/exam/** directory using vim
6. **Submit** when you've implemented and tested your solution

Remember: Every AI agent that executes code is using these exact primitives. You're learning the foundation of how AI systems interact with computers!

---

**Good luck! 🚀**
