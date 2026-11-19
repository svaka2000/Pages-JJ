# Community

A phone-first members app for an organization: one-way updates from its staff, a group chat
for each part of its membership, direct messages, a calendar, polls, a review queue for
moderators and exportable records. It's built from other OCS systems rather than beside
them, the way Courses puts lessons, chat and the calendar together for a class.

The first setup is a demo for Spark Growth Ventures (SGV), a venture firm whose investors
(limited partners, or LPs) invest deal by deal through "series". It runs at
`/community/sgv-demo/`. Every member, series, message, document and poll in it is made up,
and it runs in the browser with no backend.

## What it's built from

| Part | OCS system it uses |
| --- | --- |
| Group chats and direct messages | Messages: `createThread` (thread.js), the same pane `/dm` and the chat embeds use, with its composer, replies, edits, deletes and Add to calendar |
| Updates (staff to members) | The course announcement channel model, drawn by Messages' `createMessageLog`, read-only for members like the UI Builder's announcements block |
| Events on updates | Courses' `[[event:...]]` markers (`calendar-model.js`) |
| Calendar | Courses' week view (`calendar-feed.js` `mountWeekView`), given plain weeks |
| Add to calendar | Messages' dialog (`schedule-dialog.js`) |
| Replies to an update | Messages' reply marker (`chat-reply.js`), posted into the member's group |
| Polls | The microblog's surveys: `getSurveyResults`, `normalizeSurveyOptions`, `[[microblog:vote]]` replies |
| Poll choices | Profile's picker cards (`ocs__hub-card`) |
| Roles | Spring's role names in `Person.roles` with `hasRole` (spring#270) |
| The organization's look | The theme engine (`assets/js/user-preferences.js`, `SitePreferences.preview`) |
| Layout | The `ocs__` grammar; one addition, `ocs__tabs--fit` (in `elements/tabs`) |

The page imports every one of those modules with `{{ site.baseurl }}` and hands them to
`CommunityApp` in a `kit` object, so Community's own modules only import each other with `./`.

## Files

| File | What it does |
| --- | --- |
| `pages/sgv-demo.md` | The page (`/community/sgv-demo/`): the app bar, the tabs, four dialogs, and the starter that builds the store, the backend and the app |
| `data/texts.yml` | Every word the system shows. Code holds none, so another organization rewords it here |
| `data/sgv_demo.yml` | SGV's setup: its name, colors, series, people, channels and the made-up content |
| `js/community-app.js` | `CommunityApp`: who is viewing, the look, the tabs; builds each tab's view and rebuilds them all when the viewer changes |
| `js/updates-view.js` | `UpdatesView`: channel pills, the updates log, Reply in your group, polls, and the staff writer |
| `js/groups-view.js` | `GroupsView`: each series' chat (Messages' pane), the muted state, documents |
| `js/inbox-view.js` | `InboxView` and `NewMessageDialog`: direct messages under the DM rule |
| `js/calendar-view.js` | `CalendarView`: the Courses week view and a Coming up list |
| `js/review-view.js` | `ReviewView`: reports and actions, updates waiting for approval, the log, records export |
| `js/reply-dialog.js`, `js/report-dialog.js` | The Reply in your group and Report a message dialogs |
| `js/community-roles.js` | `CommunityRoles`: LP, moderator or staff, and which tabs each gets |
| `js/dm-policy.js` | `DmPolicy`: who may start a direct message with whom |
| `js/channel-rules.js` | `ChannelRules`: who reads and posts in each channel, and where a reply goes |
| `js/moderation.js` | `ModerationRules`: report reasons, actions, mute lengths |
| `js/records.js` | `Records`: filters and the CSV export, with spreadsheet formulas written as text |
| `js/calendar-weeks.js` | `CalendarWeeks`: plain Monday-Friday weeks shaped like the school weeks |
| `js/brand.js` | `Brand`: the setup's colors as a theme for the engine |
| `js/demo-store.js` | `DemoStore` and `RuleError`: the demo's data and every rule a server would check |
| `js/demo-backend.js` | `DemoBackend` and `DemoSocket`: Messages' API contract and the Community calls over the store |
| `js/dom.js` | `Dom`: element builders with grammar classes, and the thread pane's markup |
| `js/texts.js` | `Texts`: words by key |
| `tests/` | Node tests for every class; `fixtures.mjs` loads the YAML through Ruby and the other systems' modules |

Pure helpers are static classes (`ChannelRules.canPost(person, channel)`), and anything with
state is an instance (`new DemoStore(setup)`), as Mr. Mortensen asked on pages#2048.

## Roles and rules

| Role | Can do |
| --- | --- |
| LP (`ROLE_LP`) | Read updates, vote, talk in their series groups, download their series' documents, message staff and moderators, report a message |
| Moderator (`ROLE_MODERATOR`) | All of that, plus the review queue: hide a message, hide and mute for 24 hours or 7 days, hide and remove from the group, dismiss |
| Staff (`ROLE_STAFF`) | All of that, plus write updates (a second staff member approves each), start polls, share documents, export records |

The rules live in the classes above and are checked in `DemoStore`, not in the views:
a view hides a control it can't use, but the store refuses the call anyway, with a status and
a reason (`errors.*` in `texts.yml` words it). That's where a real server has to check them.

- Only staff post in an updates channel, and only through a second staff member's approval.
- A series group is read, posted in and followed only by that series' members (staff and
  moderators are in every series). A muted member reads but can't post until the mute ends.
- An LP can message staff and moderators but not another LP (`dm_policy: staff-only`).
  `co-investors` would allow two LPs who share a series and have both turned it on.
- Only staff share documents in a series.
- Nothing is erased: an edit adds a version, and a deleted or hidden message keeps its text
  for the records.

## The demo backend

`DemoBackend` answers the calls Messages' `createMessagesApi` makes, in Spring's shapes, so
Messages' modules run on it unchanged:

- `currentPerson`, `groupMessages`, `sendGroupMessage`, `editGroupMessage`, `deleteGroupMessage`,
  `groupFiles`, `uploadGroupFile`, `conversations`, `startConversation`, `dmMessages`, `sendDm`,
  `editDm`, `deleteDm`, `markDmRead`, `addCalendarEvent`.
- Live changes go out as Spring's frames on `/topic/group/{id}` and `/topic/dm/{id}` through
  `DemoSocket`, which has `chat-socket.js`'s `connect`, `follow`, `unfollow`, `disconnect` and
  `isConnected`.

The Community calls are the routes a real server would add: `submitUpdate`, `pendingUpdates`,
`approveUpdate`, `polls`, `createPoll`, `vote`, `report`, `reports`, `resolveReport`,
`moderationLog`, `versions`, `exportCsv` and `calendarStore`. A Spring version would map the
Messages calls to the routes that exist today and add the rest as new routes.

## Shared changes Community would use

These belong to the systems that own them, so they're proposals, not edits here:

- **Messages:** a per-message actions hook (a Report item in each message's More menu), so
  Report sits on the message instead of in the group header.
- **Messages:** `mountGroupChat` and `mountConversation` taking an `api` and a `socket`, so
  any page can run an embedded chat on another backend. `Dom.threadPane` copies the embed's
  pane markup until then.
- **Courses:** a plain-calendar mode for the calendar card (no class periods or school
  wording), which `calendar-weeks.js` works around by handing the week view plain weeks.

## Build and test

- Registered as `systems/community` (no `:dev`, so `make dev` leaves it out). Its
  `distribution.json` publishes `pages/` to `navigation/projects/community`, `data/` to
  `_data/projects/community` and `js/` to `assets/js/projects/community`.
- `node --test _projects/systems/community/tests/*.test.mjs` (55 tests). The tests read the
  YAML with Ruby, the parser Jekyll uses, and load Courses' and the microblog's modules with
  their imports stubbed, as `tests/microblog_surveys.test.mjs` does.
- How the page looks and behaves needs a browser: the demo's checks are a Playwright script
  kept outside the repo (see the hand-over notes).

## Things to know

- The demo starts over on every reload: its data lives in the page while it's open.
- The site header still asks the local backends who is signed in and for unread counts, so
  the console shows those failures when no backend runs. Community itself makes no request.
- `DemoStore` is not access control for a real site; it shows where each check belongs.
