---
name: prevent-large-file-write
enabled: true
event: file
action: block
conditions:
  - field: content
    operator: regex_match
    pattern: (?:[^\n]*\n){100,}
---

🚫 **大文件写入被阻止**

检测到你正在尝试一次性写入超过100行的文件内容。

**为什么这很重要：**
- 大文件一次性写入容易导致写入错误
- 如果出错，整个文件内容可能丢失
- 分段写入可以更好地追踪进度和错误

**正确的做法：**
1. 使用 Write 工具写入前50行内容
2. 使用 Edit 工具的追加功能添加剩余内容
3. 或者将文件分成多个逻辑部分，分别写入

**示例：**
```
# 第一步：写入文件头部
Write tool: 写入前50行

# 第二步：追加剩余内容
Edit tool: 在文件末尾追加后续内容
```

请重新组织你的写入操作，分段完成文件创建。
