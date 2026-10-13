#!/usr/bin/env bash
# spec-mockup-design installer: put the skill where your AI agents can find it.
#
#   curl -fsSL https://raw.githubusercontent.com/lunanoir21/spec-mockup-design/main/install.sh | bash
#   bash install.sh                      pick agents interactively (detected ones are pre-selected)
#   bash install.sh --detected --yes     every agent found on this machine, no questions
#   bash install.sh --agents claude,codex,opencode --yes
#   bash install.sh --list               show known agents and whether each is detected / installed
#   bash install.sh --dry-run ...        show what would happen, change nothing
#   bash install.sh --uninstall [...]    remove the links THIS installer made (never touches anything else)
#   bash install.sh --instructions ...   also add a one-line pointer to the agent's AGENTS.md / GEMINI.md
#   bash install.sh --copy ...           copy files instead of symlinking (for systems without symlinks)
#
# Safe by design: never overwrites an existing entry, never deletes anything except symlinks it created
# (and only with --uninstall). The single source of truth is ~/.agents/skills/spec-mockup-design.
set -euo pipefail

NAME="spec-mockup-design"
REPO="https://github.com/lunanoir21/spec-mockup-design"
BASE="${SKILLS_HOME:-$HOME/.agents/skills}"
MARK="<!-- spec-mockup-design -->"

# id | label | skills dir(s, ':' separated) | detect path | instructions file
AGENTS=(
  "claude|Claude Code|$HOME/.claude/skills|$HOME/.claude|"
  "codex|Codex CLI|$HOME/.codex/skills|$HOME/.codex|$HOME/.codex/AGENTS.md"
  "opencode|opencode|$HOME/.config/opencode/skills|$HOME/.config/opencode|$HOME/.config/opencode/AGENTS.md"
  "gemini|Gemini CLI|$HOME/.gemini/skills|$HOME/.gemini|$HOME/.gemini/GEMINI.md"
  "antigravity|Antigravity (agy)|$HOME/.gemini/config/skills|$HOME/.gemini/antigravity-cli|"
  "cursor|Cursor|$HOME/.cursor/skills|$HOME/.cursor|"
  "kiro|Kiro|$HOME/.kiro/skills|$HOME/.kiro|"
  "qwen|Qwen Code|$HOME/.qwen/skills|$HOME/.qwen|"
  "zcode|zcode|$HOME/.zcode/skills|$HOME/.zcode|"
  "pi|pi|$HOME/.pi/agent/skills:$HOME/.pi/skills|$HOME/.pi|"
  "qoder|Qoder|$HOME/.qoder/skills|$HOME/.qoder|"
  "grok|Grok CLI|$HOME/.grok/skills|$HOME/.grok|"
  "hermes|Hermes|$HOME/.hermes/skills|$HOME/.hermes|"
  "jcode|jcode|$HOME/.jcode/skills|$HOME/.jcode|"
)

# ---------- ui ----------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then B=$'\e[1m'; D=$'\e[2m'; G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; C=$'\e[36m'; Z=$'\e[0m'; else B=; D=; G=; Y=; R=; C=; Z=; fi
say()  { printf '%s\n' "$*"; }
ok()   { printf '  %s✓%s %s\n' "$G" "$Z" "$*"; }
warn() { printf '  %s!%s %s\n' "$Y" "$Z" "$*"; }
die()  { printf '%s✗ %s%s\n' "$R" "$*" "$Z" >&2; exit 1; }

dry=0; yes=0; mode=install; sel_arg=""; detected_only=0; all=0; instr=0; copy=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry=1;; --yes|-y) yes=1;; --list) mode=list;; --uninstall) mode=uninstall;;
    --detected) detected_only=1;; --all) all=1;; --instructions) instr=1;; --copy) copy=1;;
    --agents) shift; sel_arg="${1:-}";; --agents=*) sel_arg="${1#--agents=}";;
    --help|-h) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) die "unknown option: $1 (try --help)";;
  esac; shift
done

# ---------- find or fetch the skill ----------
here=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; fi
if [ -n "$here" ] && [ -f "$here/SKILL.md" ]; then SRC="$here"
elif [ -f "$BASE/$NAME/SKILL.md" ]; then SRC="$BASE/$NAME"
else
  command -v git >/dev/null || die "git is required to download the skill"
  SRC="$BASE/$NAME"
  if [ $dry = 1 ]; then say "would clone $REPO -> $SRC"; else mkdir -p "$BASE"; git clone -q "$REPO" "$SRC"; ok "downloaded to $SRC"; fi
fi
# the canonical location is $BASE/$NAME: if we run from elsewhere, link it there (once)
CANON="$BASE/$NAME"
if [ "$(readlink -f "$SRC")" != "$(readlink -f "$CANON" 2>/dev/null || echo x)" ] && [ ! -e "$CANON" ] && [ "$mode" = install ]; then
  if [ $dry = 1 ]; then say "would link $CANON -> $SRC"; else mkdir -p "$BASE"; ln -s "$SRC" "$CANON"; ok "linked $CANON -> $SRC"; fi
fi
[ -e "$CANON" ] && SRC="$(readlink -f "$CANON")" || true

# ---------- helpers ----------
field() { local IFS='|'; local a=($1); echo "${a[$2]:-}"; }
is_detected() { [ -e "$(field "$1" 3)" ]; }
dirs_of() { local IFS=':'; echo $(field "$1" 2); }
installed_in() {  # prints dirs where our link/copy exists
  local d; for d in $(dirs_of "$1"); do { [ -e "$d/$NAME/SKILL.md" ] || [ -L "$d/$NAME" ]; } && echo "$d"; done; return 0
}
is_installed() { [ -n "$(installed_in "$1")" ]; }

if [ "$mode" = list ]; then
  say "${B}Known agents${Z}"
  for a in "${AGENTS[@]}"; do
    st="${D}not found${Z}"; is_detected "$a" && st="${G}detected${Z}"; is_installed "$a" && st="${G}installed${Z}"
    printf '  %-12s %-18s %b\n' "$(field "$a" 0)" "$(field "$a" 1)" "$st"
  done; exit 0
fi

# ---------- choose agents ----------
ids=(); for a in "${AGENTS[@]}"; do ids+=("$(field "$a" 0)"); done
declare -A pick
for i in "${ids[@]}"; do pick[$i]=0; done
if [ -n "$sel_arg" ]; then
  IFS=',' read -ra want <<<"$sel_arg"
  for w in "${want[@]}"; do w="${w// /}"; [[ " ${ids[*]} " == *" $w "* ]] || die "unknown agent '$w' (known: ${ids[*]})"; pick[$w]=1; done
elif [ $all = 1 ]; then for i in "${ids[@]}"; do pick[$i]=1; done
elif [ $detected_only = 1 ]; then for a in "${AGENTS[@]}"; do is_detected "$a" && pick[$(field "$a" 0)]=1; done
else
  for a in "${AGENTS[@]}"; do is_detected "$a" && pick[$(field "$a" 0)]=1; done
  if [ $yes = 0 ] && { [ -n "${SMD_INPUT:-}" ] || [ -t 0 ] || { [ -r /dev/tty ] && : </dev/tty 2>/dev/null; }; }; then
    tty_in=/dev/stdin; [ -t 0 ] || tty_in=/dev/tty; [ -n "${SMD_INPUT:-}" ] && tty_in="$SMD_INPUT"
    exec 3<"$tty_in"
    while true; do
      say ""; say "${B}spec-mockup-design${Z}  ${D}$([ "$mode" = uninstall ] && echo 'remove from' || echo 'install for')${Z}"
      say "${D}Detected agents are pre-selected. Type numbers to toggle, a = all, d = detected, n = none, Enter = go, q = quit.${Z}"
      n=0; for a in "${AGENTS[@]}"; do
        n=$((n+1)); id="$(field "$a" 0)"; mark="[ ]"; [ "${pick[$id]}" = 1 ] && mark="${G}[x]${Z}"
        tag=""; is_detected "$a" && tag="${D}detected${Z}"; is_installed "$a" && tag="${C}installed${Z}"
        printf '  %2d) %b %-18s %b\n' "$n" "$mark" "$(field "$a" 1)" "$tag"
      done
      printf '> '; read -r -u 3 ans || ans=""
      case "$ans" in
        "") break;; q|Q) say "bye"; exit 0;;
        a|A) for i in "${ids[@]}"; do pick[$i]=1; done;; n|N) for i in "${ids[@]}"; do pick[$i]=0; done;;
        d|D) for i in "${ids[@]}"; do pick[$i]=0; done; for a in "${AGENTS[@]}"; do is_detected "$a" && pick[$(field "$a" 0)]=1; done;;
        *) for t in $ans; do if [[ "$t" =~ ^[0-9]+$ ]] && [ "$t" -ge 1 ] && [ "$t" -le "${#ids[@]}" ]; then k="${ids[$((t-1))]}"; pick[$k]=$((1-${pick[$k]})); fi; done;;
      esac
    done
  fi
fi
chosen=(); for a in "${AGENTS[@]}"; do [ "${pick[$(field "$a" 0)]}" = 1 ] && chosen+=("$a"); done
[ ${#chosen[@]} -gt 0 ] || { warn "no agents selected (nothing detected? try --all or --agents claude,codex)"; exit 0; }

# ---------- uninstall ----------
if [ "$mode" = uninstall ]; then
  say "${B}Removing links to $SRC${Z}"
  for a in "${chosen[@]}"; do
    for d in $(dirs_of "$a"); do t="$d/$NAME"
      if [ -L "$t" ] && [ "$(readlink -f "$t")" = "$SRC" ]; then
        if [ $dry = 1 ]; then say "  would remove link $t"; else rm "$t" && ok "removed $t"; fi
      elif [ -e "$t" ]; then warn "$t is not a link made by this installer, left untouched"; fi
    done
  done; exit 0
fi

# ---------- install ----------
say ""; say "${B}Installing $NAME${Z} ${D}($SRC)${Z}"
fail=0
for a in "${chosen[@]}"; do
  id="$(field "$a" 0)"; label="$(field "$a" 1)"; done_one=0
  for d in $(dirs_of "$a"); do
    t="$d/$NAME"
    if [ ! -d "$d" ]; then
      if [ $dry = 1 ]; then say "  would create $d"; else mkdir -p "$d"; fi
    fi
    if [ -L "$t" ] && [ "$(readlink -f "$t")" = "$SRC" ]; then ok "$label: already linked ($t)"; done_one=1; continue; fi
    if [ -e "$t" ] || [ -L "$t" ]; then warn "$label: $t exists and is something else, left untouched"; continue; fi
    if [ $dry = 1 ]; then say "  would $([ $copy = 1 ] && echo copy || echo link) $t"; done_one=1; continue; fi
    if [ $copy = 1 ]; then cp -r "$SRC" "$t"; else ln -s "$SRC" "$t"; fi
    if [ -f "$t/SKILL.md" ]; then ok "$label: $([ $copy = 1 ] && echo copied || echo linked) -> $t"; done_one=1; else warn "$label: link created but SKILL.md not readable"; fail=1; fi
  done
  inst="$(field "$a" 4)"
  if [ $instr = 1 ] && [ -n "$inst" ]; then
    if [ -f "$inst" ] && grep -q "$MARK" "$inst"; then ok "$label: instruction pointer already in $inst"
    elif [ $dry = 1 ]; then say "  would append the pointer to $inst"
    else
      mkdir -p "$(dirname "$inst")"
      printf '\n%s\n# spec-mockup-design\n- For any request to design, mock up or sketch a UI, load `%s/SKILL.md` first and follow it. Do not claim any file or step exists unless you ran the tool and saw it.\n' "$MARK" "$CANON" >>"$inst"
      ok "$label: pointer added to $inst"
    fi
  fi
done

say ""
if [ $dry = 1 ]; then say "${Y}dry run: nothing was changed${Z}"; else
  say "${B}Done.${Z} Try this in your agent:"
  say "  ${C}Design a CPU temperature widget for my status bar. Show idle, warning and critical states.${Z}"
  say "${D}More prompts: $SRC/docs/PROMPTS.md · update later with: git -C $SRC pull${Z}"
fi
exit $fail
