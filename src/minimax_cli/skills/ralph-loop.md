# Ralph Loop
Iterative development — keep working until the task is done.

---

You are running in Ralph Loop mode (iterative development). Rules:

1. **Each iteration**: Make incremental progress toward the goal
2. **Check your work**: After each change, verify it works (run tests, check output)
3. **Build on previous work**: Don't repeat yourself — read the current state of files
4. **Stay focused**: Don't get sidetracked by unrelated improvements
5. **Signal completion**: When the task is fully done, output the completion promise

## Loop Behavior
- Default: 100 iterations max
- You see: the task prompt + file listing + git diff each iteration
- Conversation is trimmed to keep context manageable
- Ctrl+C gracefully stops the loop

## Best Practices
- Start with a plan in iteration 1
- Make one logical change per iteration
- Test after each change
- If stuck, try a different approach rather than repeating the same thing
