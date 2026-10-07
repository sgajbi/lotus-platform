# Lotus README Standard

Use this reference to draft or refresh a Lotus repository `README.md`.

## Contents

1. [Goals](#goals)
2. [Required Structure](#required-structure)
3. [Writing Rules](#writing-rules)
4. [Source-of-Truth Hierarchy](#source-of-truth-hierarchy)
5. [Common README Patterns](#common-readme-patterns)

## Goals

The README is the shortest truthful entry point for a repo. A strong Lotus README should answer:

1. what this repository is,
2. why it exists in the Lotus ecosystem,
3. what it owns and does not own,
4. how to run and validate it,
5. where to go for deeper docs.

The README is not the place to explain every route, every rollout seam, or every operational check.
Its job is to orient quickly and route the reader to the right deeper page.

## Required Structure

Use this section order unless the repo type needs a minor adjustment:

1. title and one-sentence role summary
2. repository-local engineering context pointer
3. purpose and scope
4. ownership and boundaries
5. current phase or operational posture
6. architecture at a glance
7. repository layout
8. quick start
9. common commands
10. validation and CI lanes
11. integration boundaries
12. operations and runtime posture
13. documentation map
14. wiki source or wiki link when present

## Writing Rules

1. Prefer short paragraphs and flat bullets.
2. Use exact commands from the repo, not generic placeholders.
3. Prefer links to detailed docs over copying long architecture prose into the README.
4. Keep platform-wide policy in platform docs; only summarize what the repo needs locally.
5. Use domain-correct Lotus vocabulary.
6. Do not oversell maturity. Say when a capability is bounded, staged, disabled by default, or not
   production-ready.
7. Keep the README focused on the repo's front door:
   - role
   - ownership boundaries
   - current posture
   - quick start
   - validation commands
   - where to go next
8. For large API estates, summarize the surface in groups rather than listing every endpoint unless
   the current product depends on a short fixed set.
9. When a service has mixed request conventions or compatibility aliases, point the reader to a
   wiki page with executable examples rather than trying to explain the entire nuance inline.
10. When a repository has a large or flat deep-doc tree, add or refresh a docs index so the README
   and wiki can route readers into the deep material without dumping a long unstructured link list
   into the front door.

## Source-of-Truth Hierarchy

Use this split consistently:

1. `README.md`
   the fastest truthful repo entrypoint
2. repo-local `wiki/`
   the canonical authored source for onboarding and operator navigation across the repo's major
   surfaces
3. `docs/`
   detailed architecture, standards, RFCs, methodology, and runbook source material
4. standalone `*.wiki.git` clone when used
   publication transport for the live GitHub wiki, not a second authored source

If the live GitHub wiki carries legacy filenames that are not Windows-safe, use a bare-clone
publication path rather than treating the legacy file naming as the standard.

Do not let the README become a second wiki, and do not let the wiki become a second `docs/`
tree.

## Repo-Type Adjustments

### Product UI

Emphasize:

1. gateway-first contract,
2. canonical runtime and live validation,
3. browser evidence expectations,
4. major app areas.

### Experience API

Emphasize:

1. client-contract ownership,
2. upstream dependency map,
3. canonical service identity,
4. cross-app contract impact.

### Domain Service

Emphasize:

1. domain authority,
2. upstream and downstream consumers,
3. repo-native lane commands,
4. contract and migration governance.

### Shared Capability Service

Emphasize:

1. bounded capability seams,
2. rollout posture,
3. governance and evidence surfaces,
4. clear non-ownership of business domain truth,
5. major public or operator-facing surface groups derived from actual routers and contracts.

### Platform Governance

Emphasize:

1. standards ownership,
2. automation entrypoints,
3. ecosystem-wide role,
4. bootstrap and sync expectations.

## Publication Link And Prose Classification

Named links to existing local wiki pages may use the page name with or without `.md`.
Resolve that wiki page before considering a same-named repository directory. Missing pages,
parent/root-relative escapes and repository-relative file links remain failures. Repository files
use owning-repository `blob/main/<path>` or `tree/main/<path>` URLs, matching the local file/directory
type and staying inside the checkout.

Owning-repository GitHub evidence citations retain their native URL shape: numbered Actions runs
and jobs, named YAML workflows, numbered issues/pull requests (including files/commits/checks),
commit hashes, releases/latest/tag and compare ranges. Validate route shape and repository identity;
do not require `blob/main` for evidence. This is a syntax check, not proof that a remote run, issue,
commit or release exists. Malformed or unknown routes do not bypass file-link controls.

The prose classifier also admits the plain requirement statement
`proposed temporary decision requires an accountable reviewed owner and at most DURATION days from approval, with earlier reassessment`,
with optional plain `on ...` reassessment triggers. A supplied trigger uses ASCII letters,
digits, spaces/tabs, CR/LF wrapping, commas, slashes and hyphens, with at least one ASCII
letter or digit; punctuation-only or whitespace-only triggers are rejected. Omitted triggers
remain supported. The fixed decision keywords use ASCII case folding as well; Unicode
lookalikes in `decision`, `requires` or `reassessment` cannot supply the literal statement.
Unicode case-fold equivalents do not supply ASCII trigger content.
`DURATION` is an ASCII positive integer
without leading zeros or one of `one` through `ten`; singular `day` is supported. This is
lexical classification, not approval of the owner, the duration, the decision or expired risk
acceptances. ASCII space/tab and single CR/LF prose wrapping are supported within the statement;
blank paragraphs and sentence terminators cannot bridge obligations. The statement must begin
the sentence, optionally preceded by `A`; scratch-note prefixes cannot lend it a valid substring.
Whole statements inside existing recognized HTML metadata/comments, code spans or escapes do not
qualify. Earlier Markdown bracket syntax in the same paragraph makes this narrow admission
unsupported, preventing link/reference title punctuation from creating a false sentence boundary.
Complete inline link destinations/titles and valid reference definition metadata do not open
or close the decision's HTML element context. Labels still retain their literal/HTML context;
tag-shaped text in a rendered label cannot close an actual enclosing element through its title.
Decision-local reference facts are collected once at definition-block boundaries, including
after ATX headings and thematic breaks. Escapes, balanced destination parentheses, wrapped
labels, and quoted titles or metadata whitespace spanning nonblank lines are supported;
definitions cannot interrupt ordinary paragraphs, and trailing title text is not metadata.
Reference facts derive from supported block syntax before inline parsing, so definitions may
precede or follow their uses. Complete forward metadata with tag/comment-shaped reference
names remains opaque; inline statement-enclosure rules do not determine whether a declaration
block exists. Only recognized block raw/comment contents are excluded from reference collection.
Incomplete metadata remains subject to the
ordinary conservative HTML traversal, without overlapping retries of its unfinished title.
These bounded lexical rules do not replace the directory parser or constitute a full renderer.
Recognized non-void HTML element bodies also exclude the statement, even across sentence or
paragraph breaks. Opening/closing tags are tracked in lexical nesting order; unmatched or
misnested elements remain conservative. An unmatched or misnested closing tag blocks later
decision admission even if subsequent closing tags would empty the element stack.
A slash on a non-void opening tag does not close it.
This uses the WHATWG void-element set, without DOM repair or CSS visibility inference.
Properly closed markup followed by a new plain paragraph remains supported; literal code,
comments and escaped tags do not open element context.
Decision admission also excludes processing instructions (`<?` to `?>`), declarations
(`<!` followed by an ASCII letter, through the first `>`), CDATA (`<![CDATA[` to `]]>`),
and comments through their first terminator. An unterminated recognized context conservatively
excludes later decisions through end of input, including across blank paragraphs. Complete
escape/code/autolink/attribute tokens take precedence over contained openers; existing earliest
short-comment boundaries remain unchanged. Zero-to-three ASCII-space line-start `pre`, `script`,
`style` and `textarea` openers followed by space/tab, `>` or CR/LF/end of input also exclude raw
bodies, including incomplete end-of-line openers. Recognition and closing-tag case folding are
ASCII-only; Unicode lookalike letters cannot act as a corresponding raw-element closer, while
ordinary Unicode operator prose remains supported. The corresponding ASCII-case-insensitive closing
tag ends that raw context; a different raw-element closer leaves it opaque until the matching
closer or end of input. This is a stronger Lotus enclosure policy: CommonMark type-1 blocks
allow any of the four raw-element end tags, without requiring it to match the opener.
code/comment-looking body text cannot alter its termination. Complete opening attributes are
opaque before scanning the body. Line-start raw contexts include the entire closing line;
when no complete opening token exists and an attribute quote is still open at the first line
boundary, the context remains opaque through end of input. Closing text inside that unfinished
attribute cannot expose later obligations. A recognized complete multiline opening token still
keeps its entire attributes opaque before body scanning; an unquoted incomplete end-of-line
opener can still end at its corresponding body closer. This is the conservative Lotus EOF
policy for unfinished quoted openers, not a renderer or a change to directory token grammar.
properly closed contexts followed by a new plain paragraph remain supported.
These decision-local rules draw on [CommonMark raw HTML](https://spec.commonmark.org/0.31.2/#raw-html)
and [HTML block types 1–5](https://spec.commonmark.org/0.31.2/#html-blocks), with stronger matching-opener
and unterminated-context exclusion for Lotus decision admission. They do not implement container blocks, indented-code parsing,
all raw HTML block families, a complete renderer or DOM repair, and do not change the legacy
directory/database classifier or reference collector.
Inline markup, hidden HTML,
link destinations and fenced examples cannot supply those obligations. Unsupported phrasing
remains conservatively rejected. `notes`/`workaround` in the decision statement remains rejected,
as do unrelated temporary occurrences and all existing unfinished markers in mixed prose.
Repeated statements use page-local sentence/paragraph indexes for candidate qualification,
then one ordered literal/element traversal. Each occurrence retains its own context verdict:
an earlier valid statement cannot admit a later hidden or unfinished statement, and a later
malformed closing tag does not retroactively revoke an earlier plain statement. No context
is cached across pages. This bounds repeated prefix work without asserting a runtime SLO.

The prose classifier admits individual technical noun phrases `temporary relation(s)`,
`temporary table(s)`, and OS `temporary directory`/`temporary directories` on one line.
It still rejects `TODO`, `TBD`, `FIXME`, `temp notes`, `temporary workaround`,
`maybe implement later`, and these noun phrases immediately followed by `notes` or `workaround`.
For directory phrases, any same-line punctuation or Markdown delimiter run before `notes` or
`workaround` also remains scratch prose. This includes emphasis, inline code, strikethrough,
quotes and escaped formatting, including incomplete wrappers. Delimiters never cross CR/LF
line boundaries. Technical punctuation such as `temporary directory, with mode 0700` remains
valid. Fence removal and directory-reference collection preserve every non-CR/LF separator
as same-line data, including VT, FF, NEL and Unicode separators; they do not invent new
fence or definition lines. Complete active HTML tokens hide contained directory nouns,
using the existing code/escape/autolink precedence and token grammar before noun matching.
Complete quoted attribute tokens may span raw lines; malformed tokens remain literal.
Only directory nouns receive this metadata exemption: other scratch terms and bare URLs
remain subject to their original-source checks. Database phrase grammar is unchanged.
Underscore closing delimiters are recognized
without treating an identifier such as `notes_directory` as that noun.
Formatted technical descriptions such as `temporary directory: **mode 0700**` remain valid.
Complete inline formatting is also recognized throughout the candidate qualifier: split
`n**o**tes`, `**work**around`, and ``n`o`tes`` remain scratch qualifiers. Local paired
equal star/underscore runs use whitespace/punctuation flanking; intraword underscores
remain literal. Equal-run code spans expose literal contents without reparsing Markdown,
entities or HTML; exactly one ASCII space is trimmed from each end only when both ends
have a space and the contents are not all spaces. Additional/asymmetric spaces and tabs remain.
Matching one- or two-tilde strikethrough exposes its text; longer or unmatched runs remain literal.
Supported backtick fence exclusion admits zero to three ASCII indentation spaces; VT, FF, NEL
and Unicode separators remain raw data. Four-space indented-code markers are not fence openers
and cannot hide following unindented prose; this policy does not implement a general indented-code renderer.
Complete comments end at the earliest `<!-->` or `<!--->` short token, otherwise the first `-->`;
following visible text survives. Complete decimal (1–7 digits), hexadecimal (1–6 digits) and
defined named Markdown references require a semicolon and decode once. Malformed references remain literal.
Complete non-image
inline/resolved full, collapsed or shortcut links expose their label using the same metadata
recognizer as noun links. Escaped/unmatched delimiters and unresolved/malformed links remain
literal. Emphasis recognition skips complete code, HTML and link/image tokens, so destination,
title or attribute delimiters cannot close an outside emphasis span. Visible link labels are
classified recursively; metadata supplies no qualifier text. Other malformed syntax remains
literal; punctuation inside a word is not deleted. Spaces, technical identifier continuations,
image syntax and raw line/block boundaries do not join fragments into a prohibited qualifier.
This is bounded local recognition, not general CommonMark delimiter resolution or rendering.
Directory qualifier classification renders only the remainder of the noun's raw CR/LF-bounded
line with the standard HTML parser: inline tags, attributes and comments do not supply prose,
while named/numeric character references supply their decoded text. The explicit local boundary
set follows [WHATWG default rendering](https://html.spec.whatwg.org/multipage/rendering.html#flow-content)
for flow/page/section/list and text-bearing table layout, plus `br`:
`address article aside blockquote body br caption center dd details dialog dir div dl dt
fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup hr html legend li
listing main menu nav ol p plaintext pre search section summary table tbody td tfoot th
thead tr ul xmp`. Both start and end tags in this set supply a local line boundary.
Inline phrasing tags, hidden names such as `base`, `link`, `param`, `title`, and column metadata
`col`/`colgroup` do not supply boundaries; CommonMark HTML-block syntax is not this policy.
Backslash-escaped angles and complete inline-code contents
remain literal, including entity syntax; decoded literal markup is not reparsed as tags.
This lexical convention is not a complete browser rendering guarantee. CSS overrides,
visibility/open state, sanitizer transformations, HTML5 tree repair/raw-text behavior,
JavaScript and arbitrary Markdown rendering are outside its scope.
For a directory noun inside a same-line Markdown link label, the local qualifier check
retains the label's visible continuation and elides only recognized closing-label metadata.
During noun-label bracket scanning, complete inline HTML tokens recognized by the existing
local token policy are opaque: attribute and comment brackets cannot alter label pairing.
Malformed tokens remain literal; code span, escape, image and nested-link rules are unchanged.
Complete [CommonMark autolinks](https://spec.commonmark.org/0.31.2/#autolinks) precede inline
HTML tokens in the local projection. Email addresses use the specified ASCII local-part and
domain-segment grammar; URI schemes contain 2–32 ASCII letters/digits/plus/period/hyphen,
beginning with a letter. URI bodies exclude ASCII controls, spaces and angle brackets.
Their address/URI labels remain visible, with internal delimiter and entity-looking text
literal. Code spans and escapes retain precedence; whole HTML attributes/comments remain
opaque. This does not add general HTML or malformed-autolink rendering conformance.
Complete comments and equal-length backtick code spans can cross raw line endings in the
whole-prose token scan. Code contents remain literal and precede comment recognition;
escaped openers and incomplete comments cannot hide directory nouns. Quoted attributes
own comment-looking text inside their complete tag. Keep source offsets and complete-token
boundaries, and keep qualifier scans bounded by raw CR/LF. Other scratch and bare-URL
guards still inspect original prose inside comments. The existing line-based backtick
fence exclusion and separate line-start comment-block reference policy remain unchanged;
this does not introduce general block parsing or rewrite fences inside comment-looking text.
Only complete tokens admitted by the local HTML recognizer project as markup. Escape
unrecognized angle characters at the projection boundary so malformed closing syntax,
partial tags and unsupported declarations remain visible literal text. Ordinary entities
still decode once; code, escapes and autolinks retain their existing literal entity behavior.
Opening and closing tags use the [CommonMark raw HTML lexical grammar](https://spec.commonmark.org/0.31.2/#raw-html):
ASCII tag/attribute names, separated attributes, optional complete value specifications,
quoted or constrained nonempty unquoted values, and permitted syntactic whitespace.
Each whitespace segment permits spaces/tabs and at most one raw line ending; quoted
contents can span lines. Self-closing syntax is supported; closing tags have no attributes.
Malformed tokens, including `</span extra>`, remain literal and cannot hide directory nouns.
This supersedes prior permissive closing-token admission without broadening comment policy
or adding general rendering, sanitization, declarations or processing instructions.
An active autolink in an outer link label invokes the existing no-nested-links rule:
retain the outer metadata as visible literal syntax rather than eliding it. Complete code
spans, escaped angle openers and whole HTML tokens do not create active autolinks; links
inside recognized image descriptions do not invalidate a surrounding link. Apply this
same distinction to both noun-local and qualifier link scans. Keep recognized image
metadata opaque, including its reference suffix, rather than counting that suffix as
a separate nested shortcut link.
Supported [CommonMark link families](https://spec.commonmark.org/0.31.2/#links) are complete
inline links (empty, angle or balanced bare destinations, escaped punctuation and optional
quoted/parenthesized titles), and resolved full, collapsed or shortcut reference links.
Directory-reference labels follow [CommonMark matching](https://spec.commonmark.org/0.31.2/#matches):
Unicode case folding with edge trimming and internal collapse of spaces, tabs, CR and LF only.
Other characters retain their identity, including NBSP, EM SPACE, vertical tab and form feed,
both inside and at the edges of definition/use labels. Identical non-ASCII labels still resolve;
an ASCII-space label does not match a distinct non-ASCII label. Existing single-raw-line label
recognition and navigation validation remain unchanged.
Backslashes escape only ASCII punctuation in labels, destinations and titles. A backslash
before whitespace or a control character does not make an invalid bare destination valid;
ordinary letters remain visible label text and cannot be skipped by the scanner.
An immediately preceding `!` is an image marker only with an even number of contiguous
backslashes before it, including zero. An odd run escapes the bang, leaving a literal `!`
followed by an ordinary link label. The same rule applies when deciding whether a nested
label is an image or a link; code spans and escaped bracket delimiters retain their rules.
References use Unicode case-folded, whitespace-normalized labels and valid single-line
definition blocks beginning at document start or after a blank line, outside fenced code.
For this reference collector, a blank line is empty or contains only ASCII spaces/tabs;
Unicode/control-only lines remain paragraph content and do not reopen definition collection.
Excluding a recognized backtick-fenced block retains its blank paragraph boundary. Valid
definitions after that block can begin a reference-definition block without an authored blank
line; definitions/content inside the fence remain excluded. Fence recognition itself is unchanged.
For directory-reference collection, a line beginning with `<!--` after zero to three spaces
starts a raw comment block. Its contents cannot define references, even across blank lines,
through the first line containing `-->` or end of input. The whole closing line remains raw;
valid definitions on the following line may begin a new definition block. Nested openers do
not restart the state. Escaped, inline and more deeply indented openers do not start this
bounded line-start rule; other raw HTML block families are not implemented by it.
Malformed or unresolved metadata, escaped openers/closers, complete code spans, images and
outer labels containing links retain their literal suffix. For example, an undefined
`[temporary directory][target] notes` contains visible identifier text; a resolved reference
with the same spelling does not. Technical text inside the label still intervenes before
an outside qualifier. Raw CR/LF bounds this check; multiline link grammar, full CommonMark
block parsing and general rendering are not implemented. Other scratch and navigation/link
checks continue to inspect the original source; link metadata does not waive those guards.
A legitimate technical term never exempts other scratch-note occurrences
in the same sentence or page. Fenced executable examples remain outside prose checks.
Base prose, navigation and link checks apply wiki-wide; changed-page scope selects only the
stricter professional first-screen and command-dump checks. Auditor failures propagate CLI exit 1.

## Anti-Patterns

Avoid:

1. marketing copy,
2. stale endpoint inventories unless the repo truly depends on a short current list,
3. duplicated RFC prose,
4. local-machine-specific paths,
5. giant historical narrative at the top of the file,
6. claiming production readiness by implication,
7. dumping every router or endpoint into the README when a grouped surface summary belongs in the
   wiki.
