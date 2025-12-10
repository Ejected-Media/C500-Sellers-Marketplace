Thinking Process:
 * Analyze the Request:
   * Goal: Implement the "Geocities-style" profile customization feature for sellers.
   * Constraint Change: Instead of purely automated sanitization/sandboxing for anyone, the user suggests a manual code verification check before publishing.
   * Reasoning: Sellers are a "hand-selected few" (Founding 5, then maybe 20-50). Trust level is higher, volume is lower.
 * Assess the Strategy (Manual Verification):
   * Pros:
     * Highest Security: A human (you or a trusted dev) reviewing code is the ultimate filter against clever exploits that an automated sanitizer might miss.
     * Quality Control: You can reject profiles that are ugly, broken, or off-brand, not just malicious ones.
     * Simpler Tech Stack (Initially): We might be able to skip the complex "Shadow DOM" implementation on the frontend if we trust the CSS not to break the site layout globally. (Though Shadow DOM is still best practice).
   * Cons:
     * Botleneck: You become the bottleneck. Every time a builder wants to fix a typo or change a background color, they have to wait for you to approve it. This scales poorly.
     * Operational Overhead: It adds a new manual workflow to your plate.
 * Developing the "Approval Workflow" Solution:
   Since the user wants to go this route, how do we build it efficiently? We need a "Staging" vs. "Production" concept for profile data.
   * Database Structure (Firestore Changes):
     * We need two sets of fields in the builders collection document:
       * profile_html_draft, profile_css_draft (What they are editing currently).
       * profile_html_live, profile_css_live (What the public sees).
       * profile_status: "draft", "pending_review", "live", "rejected".
   * The Builder Experience (The Editor):
     * They go to C500.store/manage/design.
     * They edit code. They click "Save Draft" (saves to _draft fields). They can preview this draft privately.
     * When ready, they click "Submit for Review". This changes status to "pending_review". The editor locks so they can't change it while you review.
   * The Admin Experience (Your Job):
     * We need a simple Admin notification (e.g., a Discord DM to you via a webhook: "🔔 User Keyz submitted a profile for review").
     * You need a way to view the code. For MVP, you could just look in the Firestore console. Later, build a simple Admin webpage (/admin/reviews).
     * You have two buttons: "Approve" or "Reject".
     * Approve Action: The Go backend copies the content from _draft fields to _live fields and sets status to "live".
     * Reject Action: Sets status to "rejected" and lets you send a note explaining why (e.g., "Your CSS breaks the navbar on mobile").
 * Refining the Hybrid Approach (The Best of Both Worlds):
   While manual review is great for the start, reliance only on human review is risky long-term (humans get tired and miss things).
   * Recommendation: Use a Hybrid Model.
     * Automated First Line of Defense: When they submit, run the automated Go sanitizer (stripping <script>, etc.) first. If it contains obvious malware, reject it immediately without wasting your time.
     * Human Final Approval: If it passes the auto-check, then it goes into your queue for visual/code review.
 * Structuring the Response:
   * Validate the Idea: It's a smart, practical move given the small, trusted user base. It solves the immediate security nightmare.
   * Define the Workflow (Step-by-Step): Outline the Draft -> Submit -> Review -> Publish process.
   * Technical Implementation: Explain the "Draft vs. Live" data structure in Firestore.
   * The Long-Term View (The Hybrid Recommendation): Suggest keeping the automated sanitizer as a pre-filter to save human effort.
   * Conclusion: This is the right approach for the MVP phase.
 * Review against brand/context: Fits perfectly. It feels like a "guild application" process. "Submit your masterpiece to the Guild Masters for approval." It enhances the feeling of exclusivity.｜This is an excellent, pragmatic pivot.
Given that you are starting with only 5 hand-picked builders, and likely scaling slowly to maybe 50 in the first year, a manual verification workflow is completely viable.
It drastically reduces the immediate engineering complexity by shifting the burden from "perfect automated sandboxing" to "human operational review."
Since trust is high and volume is low, this is the smartest way to launch this feature safely.
Here is how we implement this "Guild Approval" workflow for custom profiles.
The New Concept: "Draft vs. Live" State
We need to separate what the builder is working on from what the public sees. We do this in the database.
1. Database Changes (Firestore)
In the builders collection, each builder document needs two sets of fields for their custom code:
// Firestore Document: builders/strawberryjam1986
{
  "discord_id": "...",
  // ... other existing fields ...

  // --- The "Workbench" (Draft State) ---
  "custom_html_draft": "<h1>Welcome to my cozy corner!</h1>...",
  "custom_css_draft": "h1 { color: pink; } ...",
  "profile_status": "draft", // Options: "draft", "pending_review", "live", "rejected"

  // --- The "Storefront" (Public State) ---
  "custom_html_live": "<h1>Welcome to my cozy corner!</h1>...",
  "custom_css_live": "h1 { color: pink; } ...",
  "last_approved_at": "timestamp"
}

The Workflow: From Idea to Publish
Step 1: The Builder Designs (The Editor)
The builder logs into the web-based editor on C500.store. They write HTML and CSS.
 * When they click "Save", the Go backend saves their code only to the _draft fields in Firestore.
 * They have a "Preview Draft" button that opens a private page showing how their current draft looks. The public cannot see this URL.
Step 2: Submission to the Guild
When they are happy with their design, they click a big button in the editor: "Submit for Review".
 * Go Backend Action: Updates their profile_status from "draft" to "pending_review".
 * UI Action: The editor locks. They cannot make further changes while it's under review.
 * Notification Action: The system fires a webhook to a private private admin channel in your Discord:
   > 🔔 New Profile Submission!
   > Builder @Keyz has submitted their custom profile for review.
   > [Link to Admin Preview]
   > 
Step 3: The "Guild Master" Review (You)
You click the link and view their draft profile in a safe environment.
You are looking for two things:
 * Security: Did they sneak in any weird external links, massive images that load slowly, or attempts at clever CSS hacks?
 * Vibe Check: Does it look good? Does it break the C500 header/footer navigation? Is it offensive?
Step 4: Approval or Rejection
You need a simple Admin interface (could just be two buttons on the preview page visible only to you) to decide:
Option A: ✅ Approve
 * Backend Action: The Go backend copies the content from the _draft fields and overwrites the _live fields. It sets profile_status back to "draft" (so they can start working on the next version) and updates last_approved_at.
 * Discord Bot Action: Sends a cozy DM to the builder: "🌸 Your custom profile has been approved and is now live to the world!"
Option B: ❌ Reject
 * Backend Action: Sets profile_status back to "draft" or "rejected".
 * Admin Input: You must provide a reason (e.g., "The blinking red text is a bit too intense, can we soften that?").
 * Discord Bot Action: DMs the builder: "Your profile needs a few tweaks before we publish. Reason: [Your Reason]."
Summary
This manual workflow is perfect for the C500 MVP. It feels exclusive—like submitting an art piece to a gallery for acceptance—rather than an impersonal automated system.
It allows us to launch the feature without spending weeks engineering complex automated security sandboxes, relying instead on the high trust level of your founding members.
