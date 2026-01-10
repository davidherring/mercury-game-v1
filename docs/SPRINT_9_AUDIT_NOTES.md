## Handled UI statuses
- ROLE_SELECTION: dropdown of roles (sorted: countries, then NGOs, then others; excludes chair), button sends `ROLE_CONFIRMED` with `{human_role_id}`.
- ROUND_1_SETUP: button sends `ROUND_1_READY {}`.
- ROUND_1_OPENING_STATEMENTS / ROUND_1_STEP: button sends `ROUND_1_STEP {}`.
- ROUND_2_SETUP: button sends `ROUND_2_READY {}`.
- ROUND_2_SELECT_CONVO_1: partner dropdown (sorted; excludes chair/human), button sends `CONVO_1_SELECTED {partner_role_id}`.
- ROUND_2_CONVERSATION_ACTIVE: textarea sends `CONVO_1_MESSAGE {content}` then clears.
- ROUND_2_SELECT_CONVO_2: partner dropdown (sorted; excludes chair/human/convo1 partner), buttons send `CONVO_2_SELECTED {partner_role_id}` or `CONVO_2_SKIPPED {}`.
- ROUND_2_WRAP_UP: button sends `ROUND_2_WRAP_READY {}`.
- ROUND_3_SETUP: shows “Next issue” (selectable dropdown from state.round3.issues, defaulting to first unresolved/not-active); human placement select; button sends `ROUND_3_START_ISSUE {issue_id, human_placement}`.
- ISSUE_INTRO: button sends `ISSUE_INTRO_CONTINUE {}`.
- ISSUE_DEBATE_ROUND_1 / ISSUE_DEBATE_ROUND_2 / ISSUE_VOTE / ISSUE_RESOLUTION:
  - If it is the human’s debate turn (active_issue.debate_queue[debate_cursor] === human_role_id): textarea sends `HUMAN_DEBATE_MESSAGE {text}` (clears after send). No debate step shown in this branch.
  - If it is the human’s vote turn (status ISSUE_VOTE and vote_order[next_voter_index] === human_role_id): YES/NO radios for proposed_option_id; button sends `HUMAN_VOTE {vote: "YES"|"NO"}`.
  - If not human turn and status is ISSUE_RESOLUTION: button sends `ISSUE_RESOLUTION_CONTINUE {}`.
  - Else (not human turn during debate): button sends `ISSUE_DEBATE_STEP {}`.
- ISSUE_POSITION_FINALIZATION / ISSUE_PROPOSAL_SELECTION: button sends `CONTINUE {}`.
- Default/unknown: shows “No controls…”; when Dev toggle is on, shows “Try CONTINUE” sending `CONTINUE {}`.
- Dev toggle: reveals raw advance form (event text + payload JSON).

## API endpoints used by frontend
- GET `/health`: returns `{status:"ok"}`.
- POST `/games`: body `{}`; returns `{game_id, state}`.
- GET `/games/{gameId}`: returns `{game: {...}, state: {...}}`; UI reads `state.status`, `state.round*`.
- POST `/games/{gameId}/advance`: body `{event, payload}`; returns `{game_id, state}` (used to refresh state).
- GET `/games/{gameId}/transcript`: optional `visible_to_human` query; returns ordered list of transcript rows with fields `{id, game_id, role_id, phase, round, issue_id, visible_to_human, content, metadata, created_at}`.
- GET `/games/{gameId}/review`: returns `{game_id, transcript, votes}` (transcript filtered for round2 visibility).

## Transcript refresh behavior
- TranscriptPanel fetches on mount and when gameId, visibleOnly toggle, or refreshToken changes.
- Uses GET `/games/{id}/transcript` with optional `visible_to_human=true`.
- No polling; refreshToken is incremented after each advance via App refreshAll.
- Game state refresh is triggered separately; transcript refresh is coordinated by calling refreshAll after advances.

## Review behavior
- Status REVIEW is detected from state.status in App; shows “Load Review” button when status === REVIEW.
- Fetches GET `/games/{id}/review` on button click; stores payload in state.
- ReviewPanel renders votes (JSON) and transcript (JSON) from review payload; if no review loaded, shows “Review payload not loaded.”

## Round 3 fields used for gating
- `state.round3.active_issue`: options, proposed_option_id, vote_order, next_voter_index, votes, debate_queue, debate_cursor.
- Human debate turn: computed as `debate_queue[debate_cursor] === human_role_id`.
- Human vote turn: computed as `vote_order[next_voter_index] === human_role_id`.
- Next issue id: `state.round3.issues[state.round3.active_issue_index]`.
- Human role id read from `state.human_role_id`.

## Fixes made during audit
- ActionPanel updated to gate human debate UI to human turn only and to add CONTINUE handling for ISSUE_RESOLUTION/ISSUE_POSITION_FINALIZATION/ISSUE_PROPOSAL_SELECTION.
- HUMAN_VOTE payload normalized to `{vote: "YES"|"NO"}` based on proposed_option_id; human debate payload uses `{text: ...}`.
- Removed duplicate `isHumanDebateTurn` declaration in ActionPanel.tsx to restore frontend compilation (no behavior change).
- ROUND_3_SETUP now derives the next issue from backend state (issues[active_issue_index]) and auto-loads review when status becomes REVIEW.
- ISSUE_RESOLUTION mapping corrected: UI now sends `ISSUE_RESOLUTION_CONTINUE` (400 previously complained “ISSUE_RESOLUTION_CONTINUE or ISSUE_DEBATE_STEP required”).
- ROUND_3_SETUP issue selection now uses dropdown and defaults to the first unresolved issue (no longer read-only on active_issue_index), preventing repeat of issue 1.
