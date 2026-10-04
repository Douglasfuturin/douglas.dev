---
name: youtube-analysis
description: Use when the user wants to analyze YouTube performance, check video analytics, review content metrics, schedule YouTube videos, research YouTube competitors, find the best time to post on YouTube, manage any aspect of their YouTube channel via Metricool, or generate interactive Streamlit dashboards to visualize analytics data.
---

# Analysis — YouTube Channel Manager & Dashboards

Analyze YouTube video performance, schedule uploads, research competitors, and manage your YouTube channel using Metricool MCP tools. Generate interactive Streamlit dashboards for deeper data exploration. All recommendations grounded in real data from the channel.

## First Step: Always Get Brand Info & Load Preferences

**Every session must start with two things.** Non-negotiable.

### 1. Load User Preferences

Read `.claude/skills/youtube-analysis/preferences.md` to load known brand details, channel info, and preferences from previous sessions.

### 2. Fetch Brand Data

Call `get_brands` to retrieve brand info.

1. Extract and store:
   - **blog_id** — needed for every subsequent call
   - **timezone** — needed for scheduling and analytics (format: `America%2FNew_York` for URL params, `America/New_York` for post data)
   - Confirm YouTube is connected
2. If YouTube is not connected, inform the user and stop.

### 3. Update Preferences

At the **end of every skill invocation**, update `preferences.md` with any new information learned during the session — video performance trends, scheduling patterns, competitor insights, last interaction date.

---

## Capabilities Overview

| User Intent | Workflow |
|------------|----------|
| "How's my YouTube doing?" / "Show me my analytics" | **Channel Analytics** |
| "What videos are performing?" / "Best performing content" | **Video Audit** |
| "Schedule a video" / "Plan my next upload" | **Video Scheduling** |
| "When should I post on YouTube?" | **Optimal Timing** |
| "How are my competitors doing?" / "What are competitors posting?" | **Competitor Research** |
| "Give me a full YouTube report" | **Comprehensive Report** |
| "Build me a dashboard" / "Make an interactive report" / "Visualize my data" | **Streamlit Dashboard** |

---

## Workflow 1: Channel Analytics

**Goal:** Clear picture of how the YouTube channel is performing over a specific period.

### Process

1. **Ask for the time period** if not specified. Default to last 30 days.
2. **Pull analytics data** using `get_analytics` with `network: "youtube"`. Use `get_metrics` with `network: "youtube"` first if you need to discover available metrics.
3. **Present findings** with:
   - Key metrics (subscribers, views, watch time, impressions)
   - Trends vs. previous period when possible
   - Top-performing video callouts
   - Actionable recommendations

### Presentation Format

```
## YouTube Channel Performance — [Date Range]

**Key Metrics:**
- Subscribers: X (+/- Y)
- Views: X
- Watch Time: X hours
- Impressions: X
- CTR: X%

**Highlights:**
- [Top insight]
- [Notable trend]

**Recommendation:** [One actionable next step]
```

---

## Workflow 2: Video Audit

**Goal:** Analyze individual videos to identify what's working and what's not.

### Process

1. **Pull video data** using `get_youtube_videos` for the requested time period (format: `YYYY-MM-DD`).
2. **Rank videos by performance.** Sort by views, watch time, or engagement — whichever is most relevant to the user's question.
3. **Identify patterns** in top-performing content:
   - Common topics or themes
   - Video length (short vs. long form)
   - Thumbnail/title style
   - Publishing time/day
   - Shorts vs. standard videos
4. **Present a video audit report** with top performers, underperformers, and patterns.

### Presentation Format

```
## Video Audit — [Date Range]

### Top Performers
1. **[Video title]** — [views] views, [watch time] | [date]
   Why it worked: [analysis]
2. ...

### Underperformers
1. **[Video title]** — [views] views, [watch time] | [date]
   Why it underperformed: [analysis]

### Patterns
- Top videos shared these traits: [list]
- Weak videos shared these traits: [list]

### Recommendations
1. [Do more of X]
2. [Stop doing Y]
3. [Test Z]
```

---

## Workflow 3: Video Scheduling

**CRITICAL RULE: NEVER schedule or publish a video without explicit user permission.** Even if the user says "schedule my video for Tuesday," you must:
1. Draft the full post details (title, description, time, privacy, audience settings)
2. Present the complete draft to the user for review
3. **Wait for explicit confirmation** before calling `post_schedule_post`
4. If anything is ambiguous, ask again. When in doubt, do NOT schedule.

**Goal:** Help the user schedule YouTube video uploads.

### Process

1. **Gather video details.** Ask for anything not provided:
   - Video title (required)
   - Description text
   - Video file/media
   - Made for kids? (required — yes or no)
   - Privacy setting (public, unlisted, or private — default: public)
   - Video type (video or short — default: video)
   - Category (optional — e.g., SCIENCE_TECHNOLOGY, EDUCATION, HOWTO_STYLE)
   - Tags (optional)
   - Date and time to publish (or ask if they want the optimal time)
2. **If no time specified**, use `get_best_time_to_post` with `provider: "youtube"` to recommend the optimal time.
3. **Present the full draft** and wait for confirmation.
4. **Schedule the video** using `post_schedule_post` with this structure:

```json
{
  "providers": [{"network": "youtube"}],
  "text": "[description]",
  "youtubeData": {
    "title": "[title]",
    "type": "video",
    "privacy": "public",
    "tags": ["tag1", "tag2"],
    "category": "SCIENCE_TECHNOLOGY",
    "madeForKids": false
  }
}
```

5. **Confirm success** and show the user what was scheduled and when.

### Scheduling Checklist

Before calling `post_schedule_post`, verify:
- [ ] Date is in the future (format: `YYYY-MM-DDT00:00:00`)
- [ ] Video title is provided
- [ ] `madeForKids` is set (true or false)
- [ ] Video media is attached
- [ ] `publicationDate` includes the correct timezone
- [ ] `youtubeData` is complete

---

## Workflow 4: Optimal Timing

**Goal:** Find the best time to post YouTube videos.

### Process

1. **Determine the target timeframe.** Default to the upcoming week. Keep range to 1 week max.
2. **Call `get_best_time_to_post`** with `provider: "youtube"`, date range, blog_id, and timezone.
3. **Interpret the results.** Higher score = better time to post.
4. **Present the top 3-5 best posting times:**

### Presentation Format

```
## Best Times to Post — YouTube

Based on your audience activity data:

| Rank | Day | Time | Score |
|------|-----|------|-------|
| 1 | Tuesday | 10:00 AM | 95 |
| 2 | Thursday | 2:00 PM | 88 |
| 3 | Wednesday | 11:00 AM | 82 |

**Recommendation:** Schedule your next video for [top time].
```

---

## Workflow 5: Competitor Research

**Goal:** Analyze YouTube competitors and their content to find opportunities and benchmarks.

### Process

1. **Pull competitor data** using `get_network_competitors` with `network: "youtube"`.
2. **Pull competitor videos** using `get_network_competitors_posts` with `network: "youtube"` for content-level analysis.
3. **Analyze and compare:**
   - How do your metrics compare to competitors?
   - What video types/topics are working for competitors?
   - What upload frequency do competitors use?
   - What gaps or opportunities exist?
4. **Present findings** with clear comparisons and actionable takeaways.

### Presentation Format

```
## YouTube Competitor Analysis — [Date Range]

### Your Competitors
| Competitor | Subscribers | Views | Avg Engagement |
|-----------|------------|-------|----------------|
| @competitor1 | X | Y | Z |
| @competitor2 | X | Y | Z |
| **You** | **X** | **Y** | **Z** |

### What Competitors Are Doing Well
- [Insight 1]
- [Insight 2]

### Opportunities for You
- [Gap 1 — what competitors aren't doing that you could]
- [Gap 2]

### Top Competitor Videos
1. **[@competitor]** — [video summary] — [views, engagement]
   Takeaway: [what to learn from this]
```

---

## Workflow 6: Comprehensive Report

**Goal:** Full YouTube channel report.

### Process

1. **Get the time period** — default to last 30 days.
2. **Run channel analytics** using `get_analytics`.
3. **Pull all videos** using `get_youtube_videos`.
4. **Pull competitor data** if competitors are configured.
5. **Compile into a structured report:**

```
# YouTube Channel Report — [Date Range]

## Executive Summary
[2-3 sentence overview of channel performance]

## Channel Metrics
- Subscribers: X (+/- Y)
- Total Views: X
- Watch Time: X hours
- Impressions: X
- CTR: X%

## Top Videos
1. [Title] — [views] views, [watch time]
2. [Title] — [views] views, [watch time]
3. [Title] — [views] views, [watch time]

## Content Patterns
- What's working: [themes, formats, lengths]
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

**Goal:** Generate an interactive Streamlit dashboard that visualizes analytics data, letting the user explore metrics, filter by date, and drill into video performance.

### When to Use

- User asks for a "dashboard," "interactive report," or "data visualization"
- After a comprehensive report, to give the user an explorable version of the data
- When the user wants to compare metrics across time periods visually

### Process

1. **Gather data first.** Pull all necessary data from Metricool using the appropriate tools (analytics, videos, competitors). Store the raw data as variables.

2. **Create the dashboard file** at `workspace/{today}/analysis/{dashboard-name}.py`. Use a descriptive name based on what the dashboard shows (e.g., `workspace/{today}/analysis/youtube-performance.py`, `workspace/{today}/analysis/competitor-comparison.py`).

3. **Build the Streamlit app.** The dashboard should include:
   - **Sidebar filters:** Date range picker, metric selectors, video type filters
   - **KPI cards at the top:** Big numbers for key metrics (views, subs, watch time, CTR) with delta indicators
   - **Charts:** Use Plotly for interactive charts (line charts for trends, bar charts for comparisons, scatter plots for correlations)
   - **Data tables:** Sortable tables for video-level data with st.dataframe
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
    page_title="YouTube Analytics",
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

# --- Video Table ---
# st.dataframe() with video-level data
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
streamlit run workspace/{today}/analysis/{dashboard-name}.py
```

Tell the user the dashboard is ready and provide the local URL (usually `http://localhost:8501`). If Streamlit isn't installed, install it first:

```bash
pip3 install streamlit plotly
```

### Dashboard Types

| Request | Dashboard |
|---------|-----------|
| "YouTube dashboard" / "channel overview" | Channel performance over time — views, subs, watch time, CTR trends |
| "Video performance dashboard" | Video-level table with sorting, filtering, and per-video charts |
| "Competitor dashboard" | Side-by-side comparison charts of your channel vs. competitors |
| "Content analysis dashboard" | Patterns — best posting times, video length vs. performance, topic analysis |
| "Full dashboard" | All of the above in a multi-page Streamlit app |

### Multi-Page Dashboards

For comprehensive dashboards, use Streamlit's multi-page app pattern:

```
workspace/{today}/analysis/
  youtube-dashboard.py          # Main entry point
  pages/
    1_Channel_Overview.py
    2_Video_Performance.py
    3_Competitor_Analysis.py
    4_Content_Patterns.py
```

Each page follows the same styling rules and embeds its own data subset.

---

## Managing Scheduled Videos

### Viewing Scheduled Videos
- Use `get_scheduled_posts` with blog_id, date range, timezone, and extendedRange (default false).
- Filter to YouTube-only scheduled content.
- Present as a list showing date, time, title, and privacy setting.

### Updating Scheduled Videos
- First retrieve the scheduled post using `get_scheduled_posts` to get the post `id` and `uuid`.
- **Always confirm with the user** before making changes — show what will be modified.
- Use `update_schedule_post` with the full original post data, modifying only the changed fields.
- The date cannot be in the past.
- Video must still have a title, media, and `madeForKids` setting.

---

## General Guidelines

- **NEVER schedule or modify videos without explicit user confirmation.** Always present the full draft and wait for a clear "yes." No exceptions.
- **Always load preferences first, fetch brands second.** Read `preferences.md` then call `get_brands`. Update preferences at the end of every session.
- **YouTube only for Metricool data.** This skill is scoped to YouTube for analytics and scheduling. If the user asks about other platforms, point them to the appropriate tools or suggest using the general Metricool workflow.
- **Be specific with date ranges.** Don't default to huge ranges — start focused and expand if needed.
- **Present data visually.** Use tables, ranked lists, and clear formatting. Raw numbers without context are useless.
- **Always provide actionable recommendations.** Data without insight is just noise. Tell the user what to DO with the information.
- **Handle errors gracefully.** If a tool returns no data, tell the user clearly and suggest why (e.g., "No YouTube videos found in this date range — try expanding the dates or check that YouTube is connected.").
- **Never modify video details on errors.** If something fails validation (missing media, missing title), report the error and let the user fix it. Do not silently alter their content.
- **Dashboards are self-contained.** Always embed data directly in the Streamlit files so they work without API keys or live connections.
