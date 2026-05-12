# Knowledge

Drop plain-text files in this directory. Every `.txt` file here is read at
agent-build time and appended to each agent's system prompt — Strands'
substitute for crewAI's `TextFileKnowledgeSource`.

Best for:

- Short company / product briefs (the agent always knows who its client is)
- Stable rules, glossaries, and brand voice guidelines
- Anything you want **every** agent to treat as authoritative

Not a fit for:

- Large corpora (use a real RAG pipeline instead)
- Frequently-changing data (it's loaded once per process startup)
- Per-conversation user data (use a session manager)

Files in this directory are read in alphabetical order and concatenated
under the heading `Background knowledge (treat as authoritative for your client):`.
