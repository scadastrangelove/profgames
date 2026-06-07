# On Three Elephants

### When Our Cozy Little IT World Turns into JITI

*A sequel to ["The Creator's Manifesto"](https://habr.com/ru/articles/1025108/) and ["A Licence to Agency"](https://teletype.in/@sergey_gordey/ll9nWPNNFtR). #profgames*

---

If you read the news about our little IT world too closely, you get the faint sensation of having wandered into a fresh dispatch from Bedlam. *Dear Editor, I'm writing to you in tears, this Saturday, the whole ward pressed up against the television...*

On one side, public repositories are drowning: curl shuts off its vulnerability-report intake because a robot writes them; maintainers burn their weekends triaging hallucinations; GitHub bolts a kill switch onto its inbox like the letters editor at an asylum. On the other side, those very same robots assemble overnight what used to take a team a year, and they comb open projects for real zero-days by the bucketful. On the third side, labels are suing, data registries are putting a price tag on `robots.txt`, and the Copyright Office explains with a straight face that rearranging a couple of paragraphs and hitting "submit" is creative contribution — but the freshly generated *War and Peace* itself, that's nobody's. The frame is yours; the painting belongs to no one.

It looks like an apocalypse in a single teacup. And it is.

> **So this doesn't read like an "End Is Nigh" placard.** Underneath this text sits an event layer of 110 documented signals across seven domains: OSS, music, publishing, data commons, law, security disclosure, and cloud/runtime. From here on, facts run interleaved with metaphors and serve as examples; the full table of events, with links to primary sources and an evidence level (A — primary source exists, B — secondary, and so on), is in the [appendix](ai_oss_events.html)[^dataset]. Where a claim is contestable, there's a footnote "for the nitpickers" with a signal ID next to it. A manifesto is still a manifesto — but a checkable one.

But before we dig in, let's sort out the three elephants on whose backs stood the turtle that had this teacup sloshing around on its shell.

If you've read Pratchett, you already have the picture: a Great A'Tuin paddling through the void, elephants on its back, a world balanced on top. Ours rode on three elephants, not four — Pratchett will forgive us the missing one. Because these elephants aren't decoration. They're three conditions, and pull out any one of them and the whole contraption goes into the ditch. We lived on them for twenty years without noticing, the way you don't notice air — until it's pumped out.

---

## Elephant One: Code Used to Cost Something

Reproducing it was expensive. Not prohibitively — but enough that most people agreed to play by the rules.

A young challenger's "fresh perspective" was almost always offset by accumulated legacy: domain knowledge, gnarled business logic nobody remembers the reason for anymore, and a thin coat of anti-reversing and leak protection on top. The leak of the Windows source code did not produce new Windowses. There was plenty of code — what was missing was everything else that had grown up around the code over twenty years and that you can't carry off in an archive.

Expensive to copy means few copies. Few copies means the thief is visible from a mile off. Which means the creator collects his rent simply because the cost of labor stands between him and the freeloader. No karma police required — the cost of goods does their job.

## Elephant Two: Authorship Could Be Proven

The artifact was stable. Authorship traced easily. `git blame` worked. Copyright clung to a set of lines, and a set of lines was expensive to edit — break something and you don't know what. Sure, the bloodthirsty enterprise could haul your GPL off into its box — but it was frowned upon, it sometimes backfired, and in principle you could see it with the naked eye: here's your code, here's their product, spot the difference, there is none.

Provable origin — the second elephant. Not because people sued often. But because they *could*, and everyone knew it.

## Elephant Three: Enforcement Worked

You could reach the offender, or at least make his life miserable. Licenses weren't paper tigers. The FSF reached Cisco; BusyBox reached Verizon, Samsung, and Best Buy; Harald Welte reached D-Link and Fortinet; Stockfish reached ChessBase. It almost never ended in a Hollywood verdict, but in something duller: publish the sources, halt sales, admit the violation, pay the lawyers. But that was exactly the third elephant's strength — the market knew that if the code was visible and the origin provable, enforcement worked. In due diligence, lawyers winced at GPL and demanded explanations for how to live with it. The license had teeth — it rarely bit, but it could, and the threat of the bite disciplined the market better than any bite.

---

## Now Let's Play Some Game Theory — since we're at [profgames](https://scadastrangelove.github.io/profgames/en/) after all

The three elephants held one another up. Expensive to copy → few copies → easy to trace → easy to enforce → the creator gets his cut → deviating (stealing) doesn't pay. This is a classic Nash equilibrium: given the rules, no single player benefits from moving differently. It wasn't morality that kept the industry in line. It was the payoff structure. Behaving decently was simply cheaper than behaving badly.

The beauty of an equilibrium is that it doesn't require anyone to be good. It only requires that bad not pay off. For twenty years, it didn't.

And then all three elephants fell ill. At once.

---

## The Elephants Call In Sick

**One: agents made code practically free.** Not literally zero — but a couple of orders of magnitude over the long run, easily. And it's not just that "they code faster." That's the dullest and most wrong explanation. It's the compression of middlemen and the other effects I covered in ["ProfGames"](https://scadastrangelove.github.io/profgames/en/): the output a team of thirty used to produce is now delivered by three — and twice as fast, because the communication gap collapsed, and with it the whole attendant set of cognitive biases that ate up eighty percent of the time in coordination. Not "the tool got sharper." The geometry of the team changed. The first elephant sat down on the ground.

**Two: provenance rotted.** In "ProfGames" I spoke of *professional* provenance — who you are, what you can actually do, how you'll prove it. Now it's something else: proving authorship of the artifact itself. An agent takes your Python, rewrites it in Rust, swaps the English function names for Chinese ones along the way, and the argument that this is "the same code" becomes a problem with an infinite number of asterisks. JPlag shows one percent similarity[^jplag]. The best AI-code detectors run at accuracy "below practical usefulness" and fall apart on any transformation[^detect]. The elephant shut its eyes: it still *wants* to prove authorship, but it can no longer see what there is to prove.

**Three: Themis's scales came up empty.** Enforcement didn't break. The law is alive. GPL still does battle with the bloodthirsty enterprise; coverage is even growing. What broke is the **bridge** between law and reality — the cheap ability of an ordinary maintainer to link suspicion, proof, and lawsuit into one chain. The law works beautifully where provenance is already obvious, and stalls precisely where it's now needed. The third elephant stands on its feet, trumpets briskly, and frightens absolutely no one. The sword is there. The direction of the strike is not.

The leak of the Windows source produced no new Windowses. The leak of the Claude Code harness produced a clone overnight and the fastest-growing repository in GitHub history[^clawcode]. The difference isn't in the code. The difference is that between the two leaks, all three elephants died.

---

## Which Way the Turtle Tilts

Since the equilibrium has slid, let's play theorist again and guess which direction.

The value didn't vanish, after all. It flows. By the good old rule: commoditize the complement, and the rent moves to whatever stayed scarce. Code went to zero — so the rent will move to what's still expensive to reproduce and, crucially, concentrates that cost by its very nature.

**Hyperscalers and compute.** Agents cheapen software but not data centers, peering, or relations with the regulator. Compute, giant datasets, and distribution carry economies of scale and network effects — a built-in tendency to concentrate. So the Nash equilibrium slides not "wherever the villains want," but where the math pushes it: toward control of the chokepoints. Hence roughly 77% of the world's AI infrastructure in one country[^usshare] and on the order of 87% of AI spend among a handful of players[^hyper]. This is not a conspiracy. It's a gradient. A conspiracy would have to be organized — but here, everything flows in on its own.

It has happened before, and with this exact industry. Sand, money, and the best minds in the world once slid into a single California county — not because anyone drew up a master plan, but because the gradient of defense contracts, venture capital, and universities ran that way. The result was Silicon Valley: an industry worth trillions and scientific-technical dominance for decades. Gravity doesn't choose; it just pulls everything into the deepest dip. Right now the dip is compute, data, and orders from Uncle Sam or the Big Panda — and into it slides all the same: sand, money, the best minds. Only this time, faster.

**Data and the enclosure of the commons.** Whoever realizes his contribution is being expropriated builds a fence. Reddit sues and signs deals worth a hundred and thirty million[^reddit]. Wikipedia opens a paid channel for machines[^wiki]. RSL turns `robots.txt` from a yes/no into a licensing price list — essentially ASCAP for the web[^rsl]. The common field everyone used to walk for free is being parceled into fenced lots before our eyes.

Except there's a suspicion that the fence is single-use, and will soon be torn down: models train on synthetic data, route around, distill the work of others, and the wall someone paid a hundred and thirty million for yesterday is worth zero tomorrow. Worse — many still see support in the old elephants and diligently string barbed wire between them: licenses, conditions of use, training bans, EULA clauses. It looks solid. Only the elephants are sick. Stringing a fence between buckling supports is an artistically justified occupation, but an impractical one.

**JITI — Just-in-Time IT.** Where the cost of error is low — interfaces, glue, reports, internal automation — software stops being an artifact and becomes a service on demand: assembled on the fly, for one specific user, batch size one. Not "bought a program." But "asked, received, threw away." This is the new channel the water is flowing into.

And now the main thing — about **direction**. In the new equilibrium you're not paid for contribution. You're paid for control of the entrance. Reddit can bargain — it has mass. A major label can — it has ASCAP, BMI, GEMA, and seventy years of catalog. The lone maintainer can't. The independent musician can't. They file class actions and end up with nothing while the big players carve up a garden planted by other people's hands. Value is now proportional to bargaining power, not creation. The old equilibrium hid this asymmetry behind the cost of labor and the payout for results. The new one cynically pushes it to the limit.

---

## And Our Quiet Little IT World Is No Champion Here

We like to think we're the cutting edge, that everything scary happens to us first. Relax. Lift your eyes from your own teacup and look at the neighbors in the ward — publishing and music are going through these exact effects ahead of us.

And this isn't a lyrical digression, it's a method. Music and literature should be read as **control industries** — an early-warning system for all the "cognitive industries." Their elephants took the same hit (the cost of a copy zeroed out, origin blurred), but the cycle ran earlier and more plainly, because there was neither the illusion that "complexity protects us" nor forty years of corporate fat. You look at a neighboring industry with the same disease at a later stage — and you read your own chart in advance.

**Music shows where the rent will go.** I covered this plot separately: the industry lived through its shift in equilibrium ten years earlier. Ten years earlier, music went through the *streaming* transition: ownership of a copy (you sold an album) gave way to control of access (Spotify, subscription, taste data). And the rent went — not to the musician, but to the holder of the entrance. A million streams earns the artist a decent dinner, if they cut a good deal with the distributor.

The AI break landed on them almost in sync with us, half a year earlier. Suno, Udio, 44% of Deezer's daily uploads are slop, 75 million spam tracks pulled by Spotify in a year[^music].

**Literature shows when it starts and what it looks like.** And this we somehow try not to notice — perhaps because programmers rarely talk to writers. In February 2023, the sci-fi magazine Clarkesworld closed submissions — the editors were simply buried in AI text[^clarkes]. Cheap open intake plus the "make money on ChatGPT" economy, and the filter choked within weeks. This happened **eleven months** before Stenberg first publicly cursed the slop in the curl bug tracker[^curl]. Literature ran the whole trajectory — flood, filter overload, closing the gate — nearly a year ahead of us.

Let's put it in fiction.

> ### The Case of the Dead Authorship
> The fog that year was peculiar — yellow, warm, smelling of heated silicon. It rolled in from the west, off the sea, from the districts where second-generation Gens ([GenII](https://teletype.in/@sergey_gordey/TgxOQqSEDUF)) ran day and night. The sludge climbed the storm drains and seeped under doors. On the waterfront they just called it slop.
>
> First to go under was the little **editorial office** on the corner — small, proud, with a sign reading "hard science fiction, people warm and living, robots vintage." In February it flooded to the windowsill: in a month the inbox took in more manuscripts than in a year, and half of them reeked of silicon. The editor hung up a "closed" sign. A month later he reopened — but now a bouncer sat at the door and sniffed everyone. The bouncer was human, because the editor didn't trust the machine-sniffers: they confused their own with strangers. And so it stayed. A bouncer at the door — forever.
>
> The **Great Bazaar** across the river didn't bother to investigate — too big a flow, you can't sniff everyone. It hung up a notice: "confess for yourself, slop or flesh," set a quota — no more than three stalls a day per pair of hands — and reserved the right to throw anyone out without trial. Few confessed, naturally. The Bazaar knew. The Bazaar didn't care; the public laps it up.
>
> The **Great House** on the hill held out longest — it had a name, a reputation, oak doors. It would buy a manuscript off the street, raise a fuss, sell the print run. And then a rumor crawled through the alleys, the crowd on the forums brought evidence, a private sniffer issued a verdict — silicon slop — and the House, without waiting for a trial, ran the whole print run under the knife. The author, who swore he wasn't guilty — said a freelance editor had slipped in the machine lines — was thrown into the fog without severance. And in the basement of that same House, behind a steel door, its own conveyor hummed quietly: translating novels by machine, fast, and paying people as proofreaders, so nothing would smell yellow. At the door they sniffed others. In the basement they ran their own.
>
> The scholars' **White Tower** issued a forty-page charter: anyone who let a machine into their work was obliged to confess. Everyone signed the charter. A handful confessed. The Tower pretended not to notice.
>
> The detective working the case understood, toward dawn, that he'd been chasing the wrong thing. He'd spent the whole time asking "who wrote it" — and finding no one: the sniffers lied, the evidence washed away in the fog, author and editor pointed at each other. And then it hit him that the corpse on the table *was* the question "who wrote it." It died of its own accord. The crowd on the waterfront didn't care whose hand wrote the dime novel it swallowed by the fistful — as long as it went down. The neon sign HUMAN MADE warmed the hearts of the few still walking that alley, but the alley was emptying.
>
> The real question is a different one. Not "who wrote it," but "who collects the spoils when it goes boom." And the detective didn't like the answer: not the author. The bonus goes to whoever holds the door. The one with the key to the gate through which all the fog and all the turnover flows. The author's name fades. The name of whoever holds the entrance stays on all the paperwork.

*These were writers. But swap "manuscript" for "pull request," "editorial office" for "maintainer," and "Great House" for hyperscaler — and you already know how our season ends. The neighbors played it out a year early and kindly left us the recording.*

---

## The Platform Strikes Back

And once you understand this, the headlines read differently — the ones about Microsoft and Anthropic fighting code leaks and zero-day disclosures, bolting on conditions, threatening, revoking access[^platformwars]. It's presented as protection of intellectual property. In fact it's a frantic attempt to use platform power — exactly like cancelling the monetization of AI covers on streaming. In both cases the logic is the same: defend the familiar path the money always flowed down.

The trouble is that in the new equilibrium such a move works for three months, and then accelerates exactly what they feared. Block one channel — demand floods into three new ones. Revoke access — out comes an open-weights analog. Every attempt by the platform to hold the old monetization model by force adds an argument for bypassing the platform entirely. You're not patching the dam. You're teaching the water to find a new channel, and it learns fast.

---

## The Middleman Is Dead. Long Live the Middleman.

Now to the practical side — because so far this all sounds like a description of theoretical games of elephants and turtles on a substrate of barbed wire, whereas what actually interests us is what happens to the market and the paycheck.

The compression of middlemen I covered in "ProfGames" hits the vertical of the team: between the idea and the code, links get removed, thirty people collapse into three, the middle-management status-router turns out to be unnecessary — the agent closed the communication gap and the layer evaporated. But the very same force works not only inside the team. It works on the market. And there, the middlemen are far more numerous than in any team.

Between the one who creates value and the one who consumes it, a long feeding trough of layers has grown. Each lived on a single gap and charged a margin for it — and the sums there, just so you grasp the scale, are thoroughly indecent[^markets]. The distributor — for logistics and warehousing: tech distribution is on the order of 200 billion dollars a year. The reseller and the VAR — for "I'll bring the client, package it for the local market." The systems integrator — for "it won't fly on its own, we'll implement it over two years": systems integration is around half a trillion. The consultant — for "we know how to configure this gnarly thing": IT consulting is over 100 billion. The staffing galley — for "we'll sell you man-hours": 85 to 250 billion, depending how you count. The arbiter-analyst with the magic quadrant — for "we'll tell the market what to buy": Gartner alone takes about 6 billion a year off that role. They all sold the bridging of a gap. The agent collapses those gaps one by one: compare fifty solutions — a minute; configure — a prompt; localize — on the fly; bring the client — he showed up himself through the marketplace.

**Let's prophesy.** Software distributors and resellers die first — pure margin layers with no value of their own. The army of implementation consultants shrinks to a thin layer of those who take on *responsibility* for it flying (rather than the *work* of making it fly). The arbiter-analysts lose their role as oracle of choice — the agent compares for itself, no quadrant subscription required. "We sell heads" staffing crumbles along with the shrinking of teams. The middle of the sales chain — those sturdy firms of two hundred to two thousand people — drops out first, because it has neither the cheapness of slop below nor the time-anchors of the platform above. Add these segments up and you get more than a trillion dollars a year of pure intermediary turnover currently standing on the path between creator and consumer. That trillion is what's now set in motion.

The margin of the collapsed middlemen does not return to the creator — though that's exactly what we're sold under the banner of "AI democratizes, now the author gets his due." He won't. A dozen small middlemen collapse not into zero, but into one — into the platform-entrance, the marketplace, the cloud, the control tower. And this single remaining middleman collects the combined rent of all the dead ones. The king is dead, long live the king — only now there's just one for the whole country. Or for the whole planet?

**Now *that's* a twist.**

Music showed it literally, no embellishment. They killed the record store, the distributor, the disc kiosk — a whole chain of layers between musician and listener. The money from that didn't go to the musician. It went to Spotify and TikTok. The middleman didn't disappear — it changed, grew larger, and became the only one. The musician, who supposedly had the "parasite middlemen removed," earns enough off a million streams to mix a couple of tracks. All the freed-up margin settled at the point of entry.

In software it'll be exactly so. The sales chain will wither — and it'll be sold as the creator's victory. But the rent from all the withered links will gather in the hyperscaler, in the agent marketplace, and in that same trusted box through which everything now passes. There were many middlemen, and each charged for his own gap. One is left — and he charges no longer for the gap, but for the entrance.

---

## The Redistribution of Rent

Let's pull it into one picture, because everything proceeds from here — and everyone comes here, to the watering hole, for their paycheck.

The rent has moved away from the artifact. It's no longer in *what* you made — anyone can make it, and fast. It's in what takes **time and mass** to accumulate and therefore can't be reproduced by a prompt: compute, proprietary data, network, reputation, the assembly point, control of the entrance. Artifacts sped up. Time didn't. A concert still lasts two hours, trust is still built over years, and long data by definition can't be gathered faster than the span that makes it long.

The premium freed from the collapsed middlemen doesn't return to the creator and doesn't evaporate — it migrates to two poles. Downward it drains into free slop: everything that was "decent and nameless" is now generated for nothing. Upward — to the incompressible: to the name, the network, the data, the cost of implementation and responsibility, to that single middleman who holds the entrance. The middle is left with nothing — neither the cheapness of slop below nor the time-anchors of the top. The market turns inside out: the bottom cheapens to zero, the ceiling grows dearer, and the floor most people stood on falls through.

This hurts equally those already in the market and those just entering. The old players have their time-anchors accumulated. The new ones don't, and you can't buy them — you can only wait them out. Anyone can produce now. Only a few collect rent — the ones sitting at the entrance. The collapse of the junior-hiring funnel isn't a local misfortune for recruiters; it's an early symptom of the same fracture.

And from here, too, comes the answer to the fashionable question. Many are eagerly tallying the losses of the AI hyperscalers: how on earth will they recoup their trillions on twenty-dollar subscriptions? They won't. Subscriptions aren't what they're aiming at. They'll simply devour the entire IT industry — which is, mind you, a market on the order of 6 trillion dollars a year[^itmarket]. The twenty-dollar subscription isn't a business model, it's an entry ticket that walks you inside while, out back, they digest the distributors, integrators, staffing firms, and half the licensing revenue. Don't count subscription revenue. Count what slice of the six-trillion-dollar pie migrates to whoever holds the entrance.

**"A Licence to Agency" isn't about the AI's lovely subjecthood.** It's like a licence to kill in a spy thriller. Someone gets the right to commit full agency upon your code — operationally, brazenly, in broad daylight — and nothing happens to him for it. He takes it, rewrites it, swaps the language and five names, ships it under his own brand. No one can prove a thing. THEY WON'T DO ANYTHING. Once, that licence had to be bought with the price of labor — rewriting was expensive, and time-is-money kept a finger on the trigger. Now the licence is issued for free, to everyone. Agent 007 with a licence for wet work on any repository.

But there's a second agency — the one that *issues* the licences and pays the agent. Access to the chokepoint is controlled by whoever holds the chokepoint. Whoever is admitted to the thinking-engines, to the data, to the assembly point, collects the rent. Whoever isn't admitted supplies the raw material for someone else's rent — and supplies it, as a rule, for free and with enthusiasm, feeding the machine the very thing it helped create.

And that second agency will push the idea "you don't need to own intellectual property, there's JITI" just as relentlessly as large landlords push "why own a home of your own — rent!"

What to do about all this is a subject for a separate conversation, and I've said some of it in both manifestos; I won't repeat myself.

---

If you boil it all down to one dry formula, almost a theorem, it comes out like this. **The old equilibrium rested on three things: the high cost of copying, the provability of origin, and the reachability of the offender. AI simultaneously cheapened copying, blurred origin, and shifted enforcement from law to platform. Therefore the rent goes not to whoever creates the artifact, but to whoever controls the entrance, the execution, and the trust.** Everything else in this text is an illustration of those three lines.

The three elephants didn't fall ill in turn but all at once — which is why it seems the world has gone mad, the turtle is listing wholesale, the teacup is sloshing over. But the turtle doesn't fall. It crawls into a new equilibrium where the teacup will sit level — just on different elephants, and far from our own backs. And most of us will wistfully recall the days when we "pulled the corporate oars" and "slaved for the Man" — because the galley, it turns out, was also a social elevator, an insurance policy, and a profession.

The five-legged dog has woken in the silicon sands. The sable will come, as it always does. The only question is to whom, and at whose expense.

---

[^dataset]: The full event layer (110 signals, [JSONL](ai_oss_signals.jsonl) + [interactive catalog](ai_oss_events.html) with filters by region, domain, and evidence level) — appendix to the manifesto. Each signal has an id of the form `SIG_<year>_<topic>`, a date, region, evidence level, and links to primary sources.
[^jplag]: An estimate from comparison practice (see "A Licence to Agency"); an order of magnitude, not a lab constant — the exact figure depends on language, volume, and depth of transformation.
[^detect]: `SIG_2026_AICD_BENCH_DETECTION_FAILURE`, `SIG_2025_CODEMIRAGE_LOW_FPR_COLLAPSE` — AI-code detection benchmarks; accuracy drops "below practical usefulness" and degrades under paraphrasing/transcoding.
[^clawcode]: `SIG_2026_CLAW_CODE_REWRITE_SPEED`, `SIG_2026_ANTHROPIC_CLAUDE_CODE_LEAK`. "Fastest-growing repository in GitHub history" — phrasing from reporting on the event, evidence level B (secondary sources); verify against the signal card.
[^usshare]: `market_baseline` of the event layer, aggregate of the U.S. share of AI infrastructure, Q4 — source IDC (≈77% at ≈$69.2B). Level: verified aggregate.
[^hyper]: `market_baseline`, hyperscaler share of AI spend ≈87% — rounded down to "on the order of 87%," not "close to 90%," so as not to overstate. Sources IDC/McKinsey.
[^reddit]: `SIG_2025_REDDIT_ANTHROPIC_LAWSUIT` and Reddit's data-licensing deals; the $130M figure is an order across the deals combined, not a single contract.
[^wiki]: `SIG_2025_WIKIMEDIA_TRAFFIC_DECLINE` and the launch of a paid access channel for machine consumers.
[^rsl]: `SIG_2025_RSL_LICENSING_STANDARD` — Really Simple Licensing, a licensing layer on top of `robots.txt`.
[^music]: Suno/Udio, Deezer's AI-upload share ≈44%, ≈75M spam tracks pulled by Spotify in a year — figures from "A Licence to Agency"; see also the music signals in the layer.
[^clarkes]: `SIG_2023_CLARKESWORLD_AI_SUBMISSIONS` — submissions closed, February 2023.
[^curl]: `SIG_2024_CURL_FIRST_SLOP_COMPLAINT` — first public complaint, January 2024; gap from Clarkesworld ≈11 months.
[^platformwars]: `SIG_2026_ANTHROPIC_CLAUDE_CODE_LEAK`, `SIG_2026_ANTHROPIC_DMCA_OVERREACH`, `SIG_2026_ANTHROPIC_DMCA_RETRACTION`, `SIG_2026_MS_NIGHTMARE_ECLIPSE_BAN`. On Anthropic: the Claude Code leak via npm/source map, mass DMCA and partial reversal — [TechCrunch](https://techcrunch.com/2026/04/01/anthropic-took-down-thousands-of-github-repos-trying-to-yank-its-leaked-source-code-a-move-the-company-says-was-an-accident/) and the [GitHub DMCA registry](https://github.com/github/dmca/blob/master/2026/03/2026-03-31-anthropic.md). On Microsoft: Nightmare-Eclipse, 6 Windows zero-days, and retreat after backlash — [The Register](https://www.theregister.com/security/2026/06/02/microsoft-reaches-for-olive-branch-after-public-dustup-with-0-day-researcher/5249945), [The Record](https://therecord.media/microsoft-says-it-will-not-pursue-security-researchers-disclosure), [Windows Central](https://www.windowscentral.com/microsoft/microsoft-backs-off-legal-threats-against-windows-security-researchers).
[^markets]: Estimates of intermediary markets (2024–2026, aggregators Mordor/IDC/Precedence/Grand View/Market.us and others): tech distribution ≈$108–208B; systems integration ≈ half a trillion; IT consulting ≈$74–313B (highly definition-dependent); IT staffing/outstaffing ≈$85–254B; Gartner revenue ≈$6B. Figures vary across agencies — orders of magnitude are given, not exact values.
[^itmarket]: `market_baseline`: global IT market 2026 ≈$6.31T (Gartner, updated). Within it, IT services ≈$1.87T, of which professional services (SI + consulting) are the majority.
