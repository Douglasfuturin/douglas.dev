---
name: instagram-analysis
description: Use when the user wants to analyze Instagram performance, check post analytics, review content metrics, schedule Instagram posts, research Instagram competitors, find the best time to post on Instagram, manage any aspect of their Instagram account via Metricool, or generate interactive Streamlit dashboards to visualize analytics data.
---

# Analysis — Instagram Account Manager & Dashboards

Analyze Instagram post performance, schedule content, research competitors, and manage your Instagram account using Metricool MCP tools. Generate interactive Streamlit dashboards for deeper data exploration. All recommendations grounded in real data from the account.

## First Step: Always Get Brand Info & Load Preferences

**Every session must start with two things.** Non-negotiable.

### 1. Load User Preferences

Read `.claude/skills/instagram-analysis/preferences.md` to load known brand details, account info, and preferences from previous sessions.

### 2. Fetch Brand Data

Call `get_brands` to retrieve brand info.

1. Extract and store:
   - **blog_id** — needed for every subsequent call
   - **timezone** — needed for scheduling and analytics (format: `America%2FNew_York` for URL params, `America/New_York` for post data)
   - Confirm Instagram is connected
2. If Instagram is not connected, inform the user and stop.

### 3. Update Preferences

At the **end of every skill invocation**, update `preferences.md` with any new information learned during the session — post performance trends, scheduling patterns, competitor insights, last interaction date.

---

## Capabilities Overview

| User Intent | Workflow |
|------------|----------|
| "How's my Instagram doing?" / "Show me my analytics" | **Account Analytics** |
| "What posts are performing?" / "Best performing content" | **Post Audit** |
| "Schedule a post" / "Plan my next carousel" | **Post Scheduling** |
| "When should I post on Instagram?" | **Optimal Timing** |
| "How are my competitors doing?" / "What are competitors posting?" | **Competitor Research** |
| "Give me a full Instagram report" | **Comprehensive Report** |
| "Build me a dashboard" / "Make an interactive report" / "Visualize my data" | **Streamlit Dashboard** |

---

## Workflow 1: Account Analytics

**Goal:** Clear picture of how the Instagram account is performing over a specific period.

### Process

1. **Ask for the time period** if not specified. Default to last 30 days.
2. **Pull analytics data** using `get_analytics` with `network: "instagram"`. Use `get_metrics` with `network: "instagram"` first if you need to discover available metrics.
3. **Present findings** with:
   - Key metrics (followers, reach, impressions, engagement)
   - Trends vs. previous period when possible
   - Top-performing post callouts
   - Actionable recommendations

### Presentation Format

```
## Instagram Account Performance — [Date Range]

**Key Metrics:**
- Followers: X (+/- Y)
- Reach: X
- Impressions: X
- Engagement Rate: X%
- Profile Visits: X

**Highlights:**
- [Top insight]
- [Notable trend]

**Recommendation:** [One actionable next step]
```

---

## Workflow 2: Post Audit

**Goal:** Analyze individual posts to identify what's working and what's not.

### Process

1. **Pull post data** using `get_instagram_reels` and/or other Instagram content endpoints for the requested time period (format: `YYYY-MM-DD`).
2. **Rank posts by performance.** Sort by reach, engagement, saves, or shares — whichever is most relevant to the user's question.
3. **Identify patterns** in top-performing content:
   - Common topics or themes
   - Post format (carousel, Reel, single image, Story)
   - Caption style and length
   - Publishing time/day
   - CTA type used
4. **Present a post audit report** with top performers, underperformers, and patterns.

### Presentation Format

```
## Post Audit — [Date Range]

### Top Performers
1. **[Post description/caption hook]** — [reach] reach, [engagement] interactions | [date]
   Why it worked: [analysis]
2. ...

### Underperformers
1. **[Post description/caption hook]** — [reach] reach, [engagement] interactions | [date]
   Why it underperformed: [analysis]

### Patterns
- Top posts shared these traits: [list]
- Weak posts shared these traits: [list]

### Recommendations
1. [Do more of X]
2. [Stop doing Y]
3. [Test Z]
```

---

## Workflow 3: Post Scheduling

**CRITICAL RULE: NEVER schedule or publish a post without explicit user permission.** Even if the user says "schedule my post for Tuesday," you must:
1. Draft the full post details (caption, media description, time, format)
2. Present the complete draft to the user for review
3. **Wait for explicit confirmation** before calling `post_schedule_post`
4. If anything is ambiguous, ask again. When in doubt, do NOT schedule.

**Goal:** Help the user schedule Instagram posts.

### Process

1. **Gather post details.** Ask for anything not provided:
   - Caption text (required)
   - Media/images (required)
   - Post type (carousel, Reel, single image, Story)
   - Date and time to publish (or ask if they want the optimal time)
2. **If no time specified**, use `get_best_time_to_post` with `provider: "instagram"` to recommend the optimal time.
3. **Present the full draft** and wait for confirmation.
4. **Schedule the post** using `post_schedule_post` with this structure:

```json
{
  "providers": [{"network": "instagram"}],
  "text": "[caption]",
  "instagramData": {
    "type": "carousel"
  }
}
```

5. **Confirm success** and show the user what was scheduled and when.

### Scheduling Checklist

Before calling `post_schedule_post`, verify:
- [ ] Date is in the future (format: `YYYY-MM-DDT00:00:00`)
- [ ] Caption text is provided
- [ ] Media is attached
- [ ] `publicationDate` includes the correct timezone
- [ ] Post type is specified

---

## Workflow 4: Optimal Timing

**Goal:** Find the best time to post on Instagram.

### Process

1. **Determine the target timeframe.** Default to the upcoming week. Keep range to 1 week max.
2. **Call `get_best_time_to_post`** with `provider: "instagram"`, date range, blog_id, and timezone.
3. **Interpret the results.** Higher score = better time to post.
4. **Present the top 3-5 best posting times:**

### Presentation Format

```
## Best Times to Post — Instagram

Based on your audience activity data:

| Rank | Day | Time | Score |
|------|-----|------|-------|
| 1 | Tuesday | 10:00 AM | 95 |
| 2 | Thursday | 2:00 PM | 88 |
| 3 | Wednesday | 11:00 AM | 82 |

**Recommendation:** Schedule your next post for [top time].
```

---

## Workflow 5: Competitor Research

**Goal:** Analyze Instagram competitors and their content to find opportunities and benchmarks.

### Process

1. **Pull competitor data** using `get_network_competitors` with `network: "instagram"`.
2. **Pull competitor posts** using `get_network_competitors_posts` with `network: "instagram"` for content-level analysis.
3. **Analyze and compare:**
   - How do your metrics compare to competitors?
   - What post types/topics are working for competitors?
   - What posting frequency do competitors use?
   - What carousel styles or Reels formats are they using?
   - What gaps or opportunities exist?
4. **Present findings** with clear comparisons and actionable takeaways.

### Presentation Format

```
## Instagram Competitor Analysis — [Date Range]

### Your Competitors
| Competitor | Followers | Avg Reach | Avg Engagement |
|-----------|----------|-----------|----------------|
| @competitor1 | X | Y | Z |
| @competitor2 | X | Y | Z |
| **You** | **X** | **Y** | **Z** |

### What Competitors Are Doing Well
- [Insight 1]
- [Insight 2]

### Opportunities for You
- [Gap 1 — what competitors aren't doing that you could]
- [Gap 2]

### Top Competitor Posts
1. **[@competitor]** — [post summary] — [reach, engagement]
   Takeaway: [what to learn from this]
```

---

## Workflow 6: Comprehensive Report

**Goal:** Full Instagram account report.

### Process

1. **Get the time period** — default to last 30 days.
2. **Run account analytics** using `get_analytics`.
3. **Pull all posts** using Instagram content endpoints.
4. **Pull competitor data** if competitors are configured.
5. **Compile into a structured report:**

```
# Instagram Account Report — [Date Range]

## Executive Summary
[2-3 sentence overview of account performance]

## Account Metrics
- Followers: X (+/- Y)
- Total Reach: X
- Impressions: X
- Engagement Rate: X%
- Profile Visits: X

## Top Posts
1. [Post hook] — [reach], [engagement]
2. [Post hook] — [reach], [engagement]
3. [Post hook] — [reach], [engagement]

## Content Patterns
- What's working: [themes, formats, CTA types]
- What's not: [underperforming patterns]

## Competitive Position
- [How you compare to competitors]
- [Gaps and opportunities]

## Recommendations
1. [Top priority action]
2. [Second priority]
3. [Third priority]
```

---

## Workflow 7: Streamlit Dashboard

**Goal:** Generate an interactive Streamlit dashboard that visualizes analytics data, letting the user explore metrics, filter by date, and drill into post performance.

### When to Use

- User asks for a "dashboard," "interactive report," or "data visualization"
- After a comprehensive report, to give the user an explorable version of the data
- When the user wants to compare metrics across time periods visually

### Process

1. **Gather data first.** Pull all necessary data from Metricool using the appropriate tools (analytics, posts, competitors). Store the raw data as variables.

2. **Create the dashboard file** at `analysis/{dashboard-name}.py`. Use a descriptive name based on what the dashboard shows (e.g., `analysis/instagram-performance.py`, `analysis/competitor-comparison.py`).

3. **Build the Streamlit app.** The dashboard should include:
   - **Sidebar filters:** Date range picker, metric selectors, post type filters
   - **KPI cards at the top:** Big numbers for key metrics (reach, engagement, followers, saves) with delta indicators
   - **Charts:** Use Plotly for interactive charts (line charts for trends, bar charts for comparisons, scatter plots for correlations)
   - **Data tables:** Sortable tables for post-level data with st.dataframe
   - **Brand styling:** Dark theme with green (#00CB5A) accent color

4. **Embed the data directly.** Since Metricool data comes from API calls (not a database), embed the fetched data as JSON/dicts directly in the Python file. This makes the dashboard self-contained — no API keys needed to view it.

5. **Run and present.** Launch the dashboard and tell the user how to access it.

### Dashboard Structure Template

```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Instagram Analytics",
    page_icon="📊",
    layout="wide",
)

# --- Brand Styling ---
st.markdown("""
<style>
    .stApp { background-color: #0A0B12; }
    [data-testid="stSidebar"] { background-color: #111218; }
    .metric-card {
        background: #111218;
        border: 1px solid #1a1b23;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: #FFFFFF; }
    .metric-delta-positive { color: #00CB5A; }
    .metric-delta-negative { color: #FF4444; }
    .metric-label { color: #888; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# --- Data (embedded from Metricool API) ---
DATA = {
    # Paste fetched data here as Python dicts/lists
}

# --- Sidebar Filters ---
st.sidebar.title("Filters")
# Date range, metric selectors, etc.

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
# st.metric() for each KPI

# --- Charts ---
# Plotly charts with dark theme and #00CB5A accent

# --- Post Table ---
# st.dataframe() with post-level data
```

### Styling Rules

- **Dark theme always.** Background `#0A0B12`, cards `#111218`, borders `#1a1b23`.
- **Green accent `#00CB5A`** for positive metrics, chart highlights, and primary actions.
- **Red `#FF4444`** for negative deltas and declining metrics.
- **White text** for primary content, `#888` for secondary/labels.
- **Plotly charts** should use `template="plotly_dark"` and the brand green for primary series.
- **No default Streamlit rainbow colors.** Override chart colors to use brand palette.
- **Wide layout** (`layout="wide"`) for better data density.

### Running the Dashboard

```bash
streamlit run analysis/{dashboard-name}.py
```

Tell the user the dashboard is ready and provide the local URL (usually `http://localhost:8501`). If Streamlit isn't installed, install it first:

```bash
pip3 install streamlit plotly
```

### Dashboard Types

| Request | Dashboard |
|---------|-----------|
| "Instagram dashboard" / "account overview" | Account performance over time — reach, followers, engagement, impressions trends |
| "Post performance dashboard" | Post-level table with sorting, filtering, and per-post charts |
| "Competitor dashboard" | Side-by-side comparison charts of your account vs. competitors |
| "Content analysis dashboard" | Patterns — best posting times, format performance, topic analysis |
| "Full dashboard" | All of the above in a multi-page Streamlit app |

### Multi-Page Dashboards

For comprehensive dashboards, use Streamlit's multi-page app pattern:

```
analysis/
  instagram-dashboard.py          # Main entry point
  pages/
    1_Account_Overview.py
    2_Post_Performance.py
    3_Competitor_Analysis.py
    4_Content_Patterns.py
```

Each page follows the same styling rules and embeds its own data subset.

---

## Managing Scheduled Posts

### Viewing Scheduled Posts
- Use `get_scheduled_posts` with blog_id, date range, timezone, and extendedRange (default false).
- Filter to Instagram-only scheduled content.
- Present as a list showing date, time, caption preview, and post type.

### Updating Scheduled Posts
- First retrieve the scheduled post using `get_scheduled_posts` to get the post `id` and `uuid`.
- **Always confirm with the user** before making changes — show what will be modified.
- Use `update_schedule_post` with the full original post data, modifying only the changed fields.
- The date cannot be in the past.
- Post must still have caption text and media.

---

## General Guidelines

- **NEVER schedule or modify posts without explicit user confirmation.** Always present the full draft and wait for a clear "yes." No exceptions.
- **Always load preferences first, fetch brands second.** Read `preferences.md` then call `get_brands`. Update preferences at the end of every session.
- **Instagram only for Metricool data.** This skill is scoped to Instagram for analytics and scheduling. If the user asks about other platforms, point them to the appropriate tools or suggest using the general Metricool workflow.
- **Be specific with date ranges.** Don't default to huge ranges — start focused and expand if needed.
- **Present data visually.** Use tables, ranked lists, and clear formatting. Raw numbers without context are useless.
- **Always provide actionable recommendations.** Data without insight is just noise. Tell the user what to DO with the information.
- **Handle errors gracefully.** If a tool returns no data, tell the user clearly and suggest why (e.g., "No Instagram posts found in this date range — try expanding the dates or check that Instagram is connected.").
- **Never modify post details on errors.** If something fails validation (missing media, missing caption), report the error and let the user fix it. Do not silently alter their content.
- **Dashboards are self-contained.** Always embed data directly in the Streamlit files so they work without API keys or live connections.
