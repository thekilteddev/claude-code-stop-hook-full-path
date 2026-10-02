# Linux demo: Claude Code in a container, with the Stop hook mounted read-only at /hook.
# The demo project lives at /home/dev/proj. The hook is not baked in, so you can edit it on the host.
#
#   docker build -t stop-hook-demo demo-linux
#   docker run -it --rm -v stop-hook-demo-login:/home/dev/.claude-cfg -v /absolute/path/to/this/repo:/hook:ro stop-hook-demo bash
#   claude --setting-sources project --model haiku --allowedTools 'Glob'
#
# Claude Code login state is kept in a named volume through CLAUDE_CONFIG_DIR, so you sign in once.
FROM node:22-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 git bash ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g @anthropic-ai/claude-code
RUN useradd -m -s /bin/bash dev
USER dev
ENV CLAUDE_CONFIG_DIR=/home/dev/.claude-cfg
# Created as dev BEFORE any volume mounts it: an empty named volume copies this ownership.
# Otherwise it is root-owned and the login cannot be saved.
RUN mkdir -p /home/dev/.claude-cfg
WORKDIR /home/dev/proj
RUN mkdir -p episode .claude \
 && touch episode/script.md episode/notes.md episode/clip-01.mp4 episode/clip-02.mp4 episode/cover.png episode/captions.srt
COPY --chown=dev:dev settings.json /home/dev/proj/.claude/settings.json
CMD ["bash"]
