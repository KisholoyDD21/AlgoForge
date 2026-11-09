const API = '';
const state = {
  user: null,
  route: location.hash || '#/dashboard',
  problems: { q: '', difficulty: 'All', pattern: 'All', status: 'All', platform: 'All', page: 0 },
  currentProblem: null,
  editor: null,
  editorLanguage: 'cpp',
  editorMode: 'stdin',
  draftSaveTimer: null,
  outputTab: 'output',
  authMode: 'login',
  dashboard: null,
  patterns: [],
  contests: [],
  activeContestSlug: null,
};

const templates = {
  cpp: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    // Write your solution here\n\n    return 0;\n}\n`,
  c: `#include <stdio.h>\n\nint main(void) {\n    // Write your solution here\n    return 0;\n}\n`,
  java: `import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Write your solution here\n    }\n}\n`,
  python: `def solve():\n    # Write your solution here\n    pass\n\nif __name__ == "__main__":\n    solve()\n`,
};
const languageNames = { cpp: 'C++', c: 'C', java: 'Java', python: 'Python' };
const functionTemplates = {
  'af-running-sum': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<long long> runningSum(vector<int>& nums) {
        // Return the prefix sum at every position.
        return {};
    }
};
`,
    java: `import java.util.*;

class Solution {
    public long[] runningSum(int[] nums) {
        // Return the prefix sum at every position.
        return new long[0];
    }
}
`,
    python: `from typing import List

class Solution:
    def runningSum(self, nums: List[int]) -> List[int]:
        # Return the prefix sum at every position.
        return []
`,
    c: `#include <stdio.h>
#include <stdlib.h>

long long* runningSum(int* nums, int numsSize, int* returnSize) {
    // Allocate the result with malloc and set *returnSize.
    *returnSize = 0;
    return NULL;
}
`,
  },
  'af-maximum-pair-sum': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    long long maxPairSum(vector<int>& nums) {
        // Return the sum of the two largest values.
        return 0;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public long maxPairSum(int[] nums) {
        // Return the sum of the two largest values.
        return 0L;
    }
}
`,
    python: `from typing import List

class Solution:
    def maxPairSum(self, nums: List[int]) -> int:
        # Return the sum of the two largest values.
        return 0
`,
    c: `#include <stdio.h>
#include <stdlib.h>

long long maxPairSum(int* nums, int numsSize) {
    // Return the sum of the two largest values.
    return 0;
}
`,
  },
  'af-binary-search-index': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int search(vector<int>& nums, int target) {
        // Return the target index, or -1 when it is absent.
        return -1;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public int search(int[] nums, int target) {
        // Return the target index, or -1 when it is absent.
        return -1;
    }
}
`,
    python: `from typing import List

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        # Return the target index, or -1 when it is absent.
        return -1
`,
    c: `#include <stdio.h>
#include <stdlib.h>

int search(int* nums, int numsSize, int target) {
    // Return the target index, or -1 when it is absent.
    return -1;
}
`,
  },
  'af-missing-number': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int missingNumber(vector<int>& nums) {
        // Values are distinct and belong to [0, n].
        return 0;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public int missingNumber(int[] nums) {
        // Values are distinct and belong to [0, n].
        return 0;
    }
}
`,
    python: `from typing import List

class Solution:
    def missingNumber(self, nums: List[int]) -> int:
        # Values are distinct and belong to [0, n].
        return 0
`,
    c: `#include <stdio.h>
#include <stdlib.h>

int missingNumber(int* nums, int numsSize) {
    // Values are distinct and belong to [0, n].
    return 0;
}
`,
  },
  'af-valid-parentheses': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool isValid(string s) {
        // Return true only when every bracket closes in the correct order.
        return false;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public boolean isValid(String s) {
        // Return true only when every bracket closes in the correct order.
        return false;
    }
}
`,
    python: `class Solution:
    def isValid(self, s: str) -> bool:
        # Return True only when every bracket closes in the correct order.
        return False
`,
    c: `#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int isValid(char* s) {
    // Return 1 only when every bracket closes in the correct order.
    return 0;
}
`,
  },
  'af-maximum-subarray': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    long long maxSubArray(vector<int>& nums) {
        // Return the maximum non-empty contiguous subarray sum.
        return 0;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public long maxSubArray(int[] nums) {
        // Return the maximum non-empty contiguous subarray sum.
        return 0L;
    }
}
`,
    python: `from typing import List

class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        # Return the maximum non-empty contiguous subarray sum.
        return 0
`,
    c: `#include <stdio.h>
#include <stdlib.h>

long long maxSubArray(int* nums, int numsSize) {
    // Return the maximum non-empty contiguous subarray sum.
    return 0;
}
`,
  },
  'af-longest-unique-substring': {
    cpp: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        // Return the length of the longest substring without repeats.
        return 0;
    }
};
`,
    java: `import java.util.*;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        // Return the length of the longest substring without repeats.
        return 0;
    }
}
`,
    python: `class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # Return the length of the longest substring without repeats.
        return 0
`,
    c: `#include <stdio.h>
#include <string.h>

int lengthOfLongestSubstring(char* s) {
    // Input is visible ASCII; return the longest unique substring length.
    return 0;
}
`,
  },
};
function getFunctionTemplate(problemSlug, language) {
  return functionTemplates[problemSlug]?.[language] || templates[language];
}

const navGroups = [
  { label: 'Workspace', items: [
    ['dashboard', 'Overview', '⌂'], ['problems', 'Problem set', '▤'], ['patterns', 'Patterns', '⌘'], ['roadmap', 'Learning paths', '⌁'], ['analytics', 'DSA analytics', '◴'],
  ]},
  { label: 'Practice', items: [
    ['playground', 'Playground', '▣'], ['submissions', 'Submissions', '↗'], ['contests', 'Contests', '◷'],
  ]},
  { label: 'You', items: [
    ['bookmarks', 'Saved questions', '☆'], ['profile', 'Progress & profile', '◉'],
  ]},
];

async function api(path, options = {}) {
  const config = { credentials: 'same-origin', ...options, headers: { ...(options.headers || {}) } };
  if (config.body && typeof config.body !== 'string') {
    config.headers['Content-Type'] = 'application/json';
    config.body = JSON.stringify(config.body);
  }
  const response = await fetch(API + path, config);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}
function toast(message, kind = 'success') {
  const region = document.getElementById('toast-region');
  if (!region) return;
  const node = document.createElement('div'); node.className = `toast ${kind}`; node.textContent = message;
  region.appendChild(node); setTimeout(() => node.remove(), 3600);
}
function escapeHtml(value = '') {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function slugTitle(slug) { return slug.split('/').pop().replaceAll('-', ' ').replace(/\b\w/g, c => c.toUpperCase()); }
function activeRoute() {
  const raw = location.hash.replace(/^#\/?/, '').split('?')[0];
  return raw || 'dashboard';
}
function setRoute(route) {
  location.hash = `/${route}`;
  if (location.hash === `#/${route}`) renderRoute();
}
function getRouteDetails() {
  const parts = activeRoute().split('/');
  return { page: parts[0] || 'dashboard', slug: parts.slice(1).join('/') };
}
function brandMarkSvg() {
  return `<span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 48 48" role="img"><path d="M10 34.5h28l-3.2-5.8H13.2L10 34.5Z" fill="#fff"/><path d="M14 28.5 22.8 9h4.4L36 28.5" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M18.5 21.5h11" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/><circle cx="25" cy="9" r="4.3" fill="#c9ff7a"/><circle cx="36" cy="29" r="2.8" fill="#c9ff7a"/></svg></span>`;
}
function brandIdentity(link = false) {
  const tag = link ? 'a' : 'div';
  const href = link ? ' href="#/welcome"' : '';
  return `<${tag} class="brand"${href}><span class="brand-lockup">${brandMarkSvg()}<span class="brand-name"><span class="brand-word">Algo<span>Forge</span></span><small>DSA PRACTICE WORKSPACE</small></span></span></${tag}>`;
}
function themeToggleButton(extraClass = '') {
  const isLight = document.body.classList.contains('light');
  const target = isLight ? 'dark' : 'light';
  return `<button type="button" class="theme-toggle ${extraClass}" data-action="theme" aria-label="Switch to ${target} theme" aria-pressed="${isLight}" title="Switch to ${target} theme"><span class="theme-toggle-icon" aria-hidden="true">${isLight ? '☾' : '☼'}</span><span class="theme-toggle-label">${isLight ? 'Dark' : 'Light'}</span></button>`;
}
function syncThemeControls() {
  const isLight = document.body.classList.contains('light');
  const target = isLight ? 'dark' : 'light';
  document.querySelectorAll('.theme-toggle').forEach(button => {
    button.setAttribute('aria-label', `Switch to ${target} theme`);
    button.setAttribute('aria-pressed', String(isLight));
    button.title = `Switch to ${target} theme`;
    const icon = button.querySelector('.theme-toggle-icon');
    const label = button.querySelector('.theme-toggle-label');
    if (icon) icon.textContent = isLight ? '☾' : '☼';
    if (label) label.textContent = isLight ? 'Dark' : 'Light';
  });
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', isLight ? '#f5f6f8' : '#101117');
  document.documentElement.dataset.theme = isLight ? 'light' : 'dark';
}
function applyTheme(theme, persist = false) {
  const isLight = theme === 'light';
  document.body.classList.toggle('light', isLight);
  document.body.style.backgroundColor = isLight ? '#f5f6f8' : '#101117';
  document.body.style.color = isLight ? '#202431' : '#f2f2f7';
  if (persist) {
    try { localStorage.setItem('algoforge-theme', isLight ? 'light' : 'dark'); } catch (error) { console.warn('Theme preference could not be saved:', error); }
  }
  syncThemeControls();
  if (state.editor && window.monaco) {
    try { window.monaco.editor.setTheme(isLight ? 'vs' : 'vs-dark'); } catch (error) { console.warn('Editor theme could not be changed:', error); }
  }
}
function userInitials() {
  if (!state.user) return 'G';
  return state.user.display_name.split(/\s+/).map(x => x[0]).join('').slice(0, 2).toUpperCase();
}

async function init() {
  let savedTheme = 'dark';
  try { savedTheme = localStorage.getItem('algoforge-theme') || 'dark'; } catch {}
  applyTheme(savedTheme, false);
  try {
    const me = await api('/api/me'); state.user = me.user;
  } catch { state.user = null; }
  if (!location.hash) location.hash = state.user ? '#/dashboard' : '#/welcome';
  window.addEventListener('hashchange', renderRoute);
  document.addEventListener('click', onClick);
  document.addEventListener('input', onInput);
  document.addEventListener('change', onChange);
  document.addEventListener('submit', onSubmit);
  renderRoute();
  showCookieBanner();
}

function renderShell(content, page, title) {
  const groups = state.user?.role === 'admin' ? [...navGroups, { label: 'Administration', items: [['admin', 'Admin console', '⚙']] }] : navGroups;
  const side = groups.map(group => `<div class="nav-label">${group.label}</div><div class="nav-list">${group.items.map(([key,label,icon]) => `<button class="nav-item ${page===key?'active':''}" data-nav="${key}"><span class="nav-icon">${icon}</span>${label}</button>`).join('')}</div>`).join('<div class="nav-spacer"></div>');
  const name = state.user ? escapeHtml(state.user.display_name) : 'Guest mode';
  const email = state.user ? escapeHtml(state.user.email) : 'Sign in to sync your progress';
  return `<div class="app-shell">
    <aside class="sidebar" id="sidebar">
      ${brandIdentity()}
      <nav class="sidebar-nav" aria-label="Workspace navigation">${side}</nav>
      <div class="sidebar-bottom">
        <div class="sidebar-card"><div class="mini-label">Build consistency</div><strong>One problem a day.</strong><p>Small repetitions compound into strong problem-solving instincts.</p><button data-nav="problems">Find a problem <span aria-hidden="true">↗</span></button></div>
        <div class="sidebar-user"><div class="avatar">${userInitials()}</div><div class="user-meta"><b>${name}</b><small>${email}</small></div><button class="dots" data-action="user-menu" aria-label="Account options">···</button></div>
      </div>
    </aside>
    <div class="main-area">
      <header class="topbar"><div class="breadcrumbs"><button class="icon-btn mobile-menu" data-action="mobile-menu" aria-label="Open navigation">☰</button><span>Workspace</span><span>›</span><strong>${escapeHtml(title)}</strong></div>
        <div class="top-actions"><label class="searchbox"><span aria-hidden="true">⌕</span><input id="global-search" placeholder="Search problems, patterns…" aria-label="Search problems" value="${escapeHtml(state.problems.q)}"><kbd>/</kbd></label>${themeToggleButton()}${state.user ? `<button class="icon-btn" data-action="logout" aria-label="Sign out">↪</button>` : `<button class="btn small primary" data-action="login">Sign in</button>`}</div>
      </header>
      <main id="main-content" class="${page==='problem'?'workspace-page':'page-wrap'}">${content}</main>
    </div>
  </div>`;
}

async function renderRoute() {
  if (state.editor) { state.editor.dispose(); state.editor = null; }
  const { page, slug } = getRouteDetails();
  if (page === 'login' || page === 'register') { renderAuth(page); return; }
  if (page === 'welcome') { renderLanding(); return; }
  if (page === 'privacy' || page === 'terms') { renderPolicy(page); return; }
  if (page === 'problem' && slug) { await renderProblem(slug); return; }
  if (page === 'playground') state.editorMode = 'stdin';
  if (page === 'contest' && slug) { const content = await contestDetailView(slug); document.getElementById('app-root').innerHTML = renderShell(content, 'contests', 'Contest'); return; }
  const titleMap = { dashboard: 'Overview', problems: 'Problem set', patterns: 'Patterns', analytics: 'DSA analytics', roadmap: 'Learning paths', playground: 'Playground', submissions: 'Submissions', contests: 'Contests', bookmarks: 'Saved questions', profile: 'Progress & profile', admin: 'Admin console', contest: 'Contest' };
  const title = titleMap[page] || 'Not found';
  document.title = `${title} — AlgoForge`;
  let content = '';
  try {
    if (page === 'dashboard') content = await dashboardView();
    else if (page === 'problems') content = await problemsView();
    else if (page === 'patterns') content = await patternsView();
    else if (page === 'analytics') content = await analyticsView();
    else if (page === 'roadmap') content = await roadmapView();
    else if (page === 'playground') content = playgroundView();
    else if (page === 'submissions') content = await submissionsView();
    else if (page === 'contests') content = await contestsView();
    else if (page === 'bookmarks') content = await bookmarksView();
    else if (page === 'profile') content = await profileView();
    else if (page === 'admin') content = await adminView();
    else content = notFoundView();
  } catch (error) {
    content = `<div class="empty-state"><b>Couldn't load this view</b>${escapeHtml(error.message)}<div style="margin-top:12px"><button class="btn" data-action="retry">Try again</button></div></div>`;
  }
  document.getElementById('app-root').innerHTML = renderShell(content, page, title);
  if (page === 'playground') mountEditor(null, 'playground');
}

async function dashboardView() {
  const [dash, patterns, daily, analytics] = await Promise.all([api('/api/dashboard'), api('/api/patterns'), api('/api/daily-challenge'), state.user ? api('/api/analytics') : Promise.resolve(null)]);
  state.dashboard = dash; state.patterns = patterns.items;
  const max = Math.max(1, dash.total_questions || 1);
  const percent = Math.min(100, Math.round((dash.solved / max) * 100));
  const activity = new Map((dash.activity || []).map(x => [x.date, x.count]));
  const cells = [];
  const end = new Date();
  for (let i = 181; i >= 0; i--) {
    const d = new Date(end); d.setDate(end.getDate() - i);
    const key = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
    const count = activity.get(key) || 0;
    const level = count === 0 ? 0 : count === 1 ? 1 : count === 2 ? 2 : count <= 4 ? 3 : 4;
    cells.push(`<div class="heat-cell" data-level="${level}" title="${key}: ${count} solved"></div>`);
  }
  const topPatterns = patterns.items.slice(0, 3);
  const roadmapCards = (analytics?.pattern_mastery || [])
    .filter(item => item.total > 0)
    .sort((a, b) => (a.mastery_pct - b.mastery_pct) || (b.total - a.total))
    .slice(0, 3)
    .map(item => ({ name: item.name, total: item.total, solved: item.solved, percent: item.mastery_pct }));
  const patternCards = roadmapCards.length ? roadmapCards : patterns.items.slice(0, 3).map(item => ({ name: item.name, total: item.count, solved: 0, percent: 0 }));
  const firstRecommended = await api('/api/problems?limit=1&difficulty=Easy');
  const featured = firstRecommended.items[0];
  return `<div class="page-heading"><div><div class="eyebrow">${state.user ? 'YOUR PRACTICE DESK' : 'WELCOME TO ALGOFORGE'}</div><h1>${state.user ? `Good to see you, ${escapeHtml(state.user.display_name.split(' ')[0])}.` : 'Build your problem-solving edge.'}</h1><p>${state.user ? 'Make today’s session count. Consistency beats occasional marathons.' : 'Explore a pattern-first DSA workspace. Sign in to save progress across sessions.'}</p></div><div class="heading-actions"><button class="btn" data-nav="roadmap">View roadmap</button><button class="btn primary" data-nav="problems">Browse problems <span>↗</span></button></div></div>
  <section class="grid stats-grid">
    <div class="stat-card"><div class="stat-top">Questions solved <span class="stat-icon">✓</span></div><div class="stat-value">${dash.solved}<span style="font-size:12px;color:var(--muted);font-weight:600"> / ${dash.total_questions}</span></div><div class="stat-foot"><span class="positive">${percent}%</span> of the current catalogue</div><i class="stat-accent"></i></div>
    <div class="stat-card"><div class="stat-top">Current streak <span class="stat-icon">⌁</span></div><div class="stat-value">${dash.streak}<span style="font-size:12px;color:var(--muted);font-weight:600"> days</span></div><div class="stat-foot">Longest streak: ${dash.longest_streak} days</div><i class="stat-accent"></i></div>
    <div class="stat-card"><div class="stat-top">Easy completed <span class="stat-icon">◌</span></div><div class="stat-value">${dash.easy}</div><div class="stat-foot">Foundation and fluency</div><i class="stat-accent"></i></div>
    <div class="stat-card"><div class="stat-top">Medium + hard <span class="stat-icon">⌘</span></div><div class="stat-value">${dash.medium + dash.hard}</div><div class="stat-foot">Deeper problem-solving reps</div><i class="stat-accent"></i></div>
    <div class="stat-card"><div class="stat-top">Total active days <span class="stat-icon">◷</span></div><div class="stat-value">${dash.total_active_days || 0}</div><div class="stat-foot">Days with recorded solves</div><i class="stat-accent"></i></div>
    <div class="stat-card"><div class="stat-top">Contributions <span class="stat-icon">▦</span></div><div class="stat-value">${dash.contributions || 0}</div><div class="stat-foot">Recorded problem completions</div><i class="stat-accent"></i></div>
  </section>
  <section class="grid home-grid">
    <div class="panel"><div class="panel-head"><div><div class="panel-title">Your activity</div><div class="panel-subtitle">Daily problem completions · ${dash.total_active_days || 0} active days · ${dash.contributions || 0} contributions</div></div><span class="pill violet">Last 26 weeks</span></div><div class="heatmap">${cells.join('')}</div><div class="heat-legend">Less <i></i><i></i><i></i><i></i><i></i> More</div></div>
    <div class="panel"><div class="panel-head"><div><div class="panel-title">Completion snapshot</div><div class="panel-subtitle">Progress across the question catalogue</div></div><span class="panel-link" data-nav="problems">Explore →</span></div><div class="progress-summary"><div class="ring" style="--progress:${percent}%"><span>${percent}%</span></div><div class="progress-copy"><b>${dash.solved} problems completed</b><small>${Math.max(0,dash.total_questions-dash.solved)} left in the catalogue</small><small>${state.user ? 'External solves are recorded as self-reported.' : 'Sign in to track your own progress.'}</small></div></div><div class="difficulty-bars"><div class="difficulty-row"><span>Easy</span><div class="bar-track"><div class="bar-fill easy" style="width:${Math.min(100,dash.easy/Math.max(1,dash.total_questions)*100*3)}%"></div></div><b>${dash.easy}</b></div><div class="difficulty-row"><span>Medium</span><div class="bar-track"><div class="bar-fill medium" style="width:${Math.min(100,dash.medium/Math.max(1,dash.total_questions)*100*3)}%"></div></div><b>${dash.medium}</b></div><div class="difficulty-row"><span>Hard</span><div class="bar-track"><div class="bar-fill hard" style="width:${Math.min(100,dash.hard/Math.max(1,dash.total_questions)*100*3)}%"></div></div><b>${dash.hard}</b></div></div></div>
  </section>
  <div class="section-row"><h2>Pick up where you left off</h2><span>Small, focused reps build fluency</span></div>
  <section class="grid continue-grid">${patternCards.map((item,i) => `<article class="continue-card" data-nav="patterns"><div class="card-top"><div class="pattern-icon">${['⌘','↔','⌕'][i]}</div><span class="pill">${state.user ? `${item.solved}/${item.total} solved` : `${item.total} questions`}</span></div><h3>${escapeHtml(item.name)}</h3><p>${state.user ? `${item.percent}% mastery · based on your recorded progress` : 'Explore this pattern and build your problem-solving foundation.'}</p><div class="card-progress"><span style="width:${state.user ? item.percent : 0}%"></span></div></article>`).join('')}</section>
  <div class="section-row"><h2>Daily challenge</h2><span>${escapeHtml(daily.date)} · original AlgoForge exercise</span></div>
  <section class="challenge-card"><div class="challenge-label">${daily.completed ? 'Completed with an accepted submission' : 'Today’s focused practice'}</div><h3>${escapeHtml(daily.problem.title)}</h3><p>${escapeHtml(daily.problem.pattern)} · ${escapeHtml(daily.problem.difficulty)} · ${escapeHtml(daily.problem.time_complexity || 'Complexity target available in the statement')}</p><div class="challenge-meta"><span class="pill ${daily.problem.difficulty.toLowerCase()}">${daily.problem.difficulty}</span><span class="pill">AlgoForge Originals</span><span class="pill">${daily.completed ? 'Completed' : 'Not completed yet'}</span></div><button class="btn lime" data-open-problem="${daily.problem.slug}">Open daily challenge ↗</button></section>
  ${!state.user ? `<div class="section-row"><h2>Keep your progress in one place</h2></div><div class="panel" style="display:flex;align-items:center;justify-content:space-between;gap:16px"><div><b style="font-size:12px">Create a free practice account</b><div class="panel-subtitle">Save solved status, notes, bookmarks and your activity streak.</div></div><button class="btn primary" data-action="register">Create account</button></div>` : ''}`;
}

async function analyticsView() {
  if (!state.user) return `<div class="page-heading"><div><div class="eyebrow">YOUR PERFORMANCE</div><h1>DSA analytics</h1><p>Sign in to see mastery, weak areas and recommendations.</p></div></div><div class="empty-state"><b>Your learning data belongs to your account</b><button class="btn primary" data-action="login">Sign in</button></div>`;
  const data = await api('/api/analytics');
  const metric = (label, value, sub) => `<div class="stat-card"><div class="stat-top">${label}</div><div class="stat-value">${Number(value || 0).toLocaleString()}</div><div class="stat-foot">${sub}</div><i class="stat-accent"></i></div>`;
  const masteryRows = (items) => (items || []).slice(0, 12).map(row => `<div class="mastery-row"><div class="mastery-label"><b>${escapeHtml(row.name)}</b><span>${row.solved}/${row.total} solved · ${row.attempted} attempted</span></div><div class="mastery-track"><i style="width:${Math.max(0,Math.min(100,row.mastery_pct))}%"></i></div><strong>${row.mastery_pct}%</strong></div>`).join('');
  const rows = masteryRows(data.pattern_mastery);
  const topicRows = masteryRows(data.topic_mastery);
  const focusRows = (items, emptyText) => (items || []).map(row => `<div class="recommendation-line"><span class="pill">${row.mastery_pct}%</span><div><b>${escapeHtml(row.name)}</b><small>${row.solved} of ${row.total} solved · ${row.attempted} attempted</small></div></div>`).join('') || `<div class="empty-state">${emptyText}</div>`;
  const weak = focusRows(data.weak_patterns, 'No attempted patterns are currently below the mastery threshold. Keep practising to build a reliable profile.');
  const weakTopics = focusRows(data.weak_topics, 'No attempted topics are currently below the mastery threshold.');
  const week = (data.weekly_report || []).map(day => `<div class="week-bar"><div class="week-bar-fill" style="height:${Math.max(4, Math.min(100, day.solved * 16))}%" title="${day.solved} solved"></div><b>${day.solved}</b><small>${escapeHtml(day.label)}</small></div>`).join('');
  const comparison = data.week_comparison || {};
  const change = comparison.change_pct == null ? 'No previous-week baseline' : `${comparison.change_pct > 0 ? '+' : ''}${comparison.change_pct}% vs previous week`;
  const recs = (data.recommendations || []).map(item => `<div class="analytics-recommendation"><div><b>${escapeHtml(item.title)}</b><small>${escapeHtml(item.pattern)} · ${escapeHtml(item.reason)}</small></div><span class="pill ${item.difficulty.toLowerCase()}">${escapeHtml(item.difficulty)}</span><button class="btn small" data-open-problem="${escapeHtml(item.slug)}">Practice ↗</button></div>`).join('') || `<div class="empty-state">You have completed every problem currently in the catalogue.</div>`;
  const prediction = data.prediction || {};
  return `<div class="page-heading"><div><div class="eyebrow">MEASURE WHAT YOU PRACTICE</div><h1>DSA analytics</h1><p>Metrics are derived from your saved practice records. External problem completions may be self-reported.</p></div><span class="pill violet">Personal learning profile</span></div>
    <section class="grid stats-grid analytics-metrics">${metric('Total active days', data.total_active_days, 'Unique days with recorded completions')}${metric('Contributions', data.contributions, 'Recorded problem completions')}${metric('Active days · last 7', data.consistency?.active_days_last_7, 'Consistency this week')}${metric('14-day active rate', `${data.consistency?.active_rate_14d || 0}%`, `${data.consistency?.solves_last_14d || 0} completions in 14 days`)}</section>
    <section class="analytics-grid"><div class="panel"><div class="panel-head"><div><div class="panel-title">Weekly performance</div><div class="panel-subtitle">Recorded completions over the last seven days</div></div><span class="pill violet">${comparison.current_week_solves || 0} this week</span></div><div class="weekly-chart">${week}</div><div class="analysis-note week-comparison">${escapeHtml(change)} · Previous week: ${comparison.previous_week_solves || 0} completions.</div></div><div class="panel"><div class="panel-head"><div><div class="panel-title">Learning progress prediction</div><div class="panel-subtitle">Based on your recent 14-day completion pace</div></div></div><div class="prediction-number">${prediction.estimated_days_to_complete_catalogue == null ? '—' : Number(prediction.estimated_days_to_complete_catalogue).toLocaleString()}<small>${prediction.estimated_days_to_complete_catalogue == null ? 'days unavailable' : 'estimated days to finish catalogue'}</small></div><p class="analysis-note">${escapeHtml(prediction.method || '')} Pace: ${prediction.recent_daily_solves || 0} completions/day · ${prediction.remaining_questions || 0} remaining.</p></div></section>
    <section class="analytics-grid analytics-grid-lower"><div class="panel"><div class="panel-head"><div><div class="panel-title">Pattern mastery</div><div class="panel-subtitle">Solved questions divided by all questions in each pattern</div></div><button class="btn small" data-nav="patterns">Explore patterns</button></div><div class="mastery-list">${rows || '<div class="empty-state">Problem taxonomy will appear here.</div>'}</div></div><div class="panel"><div class="panel-head"><div><div class="panel-title">Topic mastery</div><div class="panel-subtitle">Your completion percentage across DSA topics</div></div><button class="btn small" data-nav="problems">Browse topics</button></div><div class="mastery-list">${topicRows || '<div class="empty-state">Topic data will appear here.</div>'}</div></div></section>
    <section class="analytics-grid analytics-grid-lower"><div class="panel"><div class="panel-head"><div><div class="panel-title">Weak patterns</div><div class="panel-subtitle">Attempted patterns with lower completion rates</div></div></div>${weak}</div><div class="panel"><div class="panel-head"><div><div class="panel-title">Weak topics</div><div class="panel-subtitle">Topics to revisit based on your attempts</div></div></div>${weakTopics}</div></section>
    <section class="panel" style="margin-top:14px"><div class="panel-head"><div><div class="panel-title">Recommended next problems</div><div class="panel-subtitle">Prioritised toward weaker patterns and accessible difficulty</div></div></div><div class="analytics-recommendations">${recs}</div></section>`;
}
async function problemsView() {
  const f = state.problems;
  const query = new URLSearchParams({ q: f.q, difficulty: f.difficulty, pattern: f.pattern, platform: f.platform, status: f.status, limit: '30', offset: String(f.page*30) });
  const [data, patterns, platforms] = await Promise.all([api(`/api/problems?${query}`), api('/api/patterns'), api('/api/platforms')]);
  state.patterns = patterns.items;
  const rows = data.items.map(p => `<tr><td><span class="status-dot ${p.progress}">${p.progress === 'solved' ? 'Solved' : p.progress === 'in_progress' ? 'In progress' : 'To do'}</span></td><td><span class="problem-title">${escapeHtml(p.title)}</span><span class="problem-sub">${escapeHtml(p.platform)} · ${escapeHtml(p.slug)}</span></td><td><span class="pill ${p.difficulty.toLowerCase()}">${p.difficulty}</span></td><td><span class="pattern-tag">${escapeHtml(p.pattern)}</span></td><td><button class="table-link" data-open-problem="${p.slug}">Workspace ↗</button></td></tr>`).join('');
  const mobile = data.items.map(p => `<article class="mobile-problem" data-open-problem="${p.slug}"><div class="mobile-problem-top"><h3>${escapeHtml(p.title)}</h3><span class="pill ${p.difficulty.toLowerCase()}">${p.difficulty}</span></div><div class="mobile-problem-meta"><span class="pattern-tag">${escapeHtml(p.pattern)}</span><span class="status-dot ${p.progress}">${p.progress.replace('_',' ')}</span><span class="muted">${escapeHtml(p.platform)}</span></div></article>`).join('');
  const start = data.total ? f.page*30+1 : 0;
  const end = Math.min(data.total,(f.page+1)*30);
  return `<div class="page-heading"><div><div class="eyebrow">THE PRACTICE LIBRARY</div><h1>Problem set</h1><p>Find the right problem, practise a pattern and track your learning.</p></div><div class="heading-actions"><span class="pill violet">${data.total.toLocaleString()} matching questions</span></div></div>
  <div class="filter-row"><input class="filter-input" id="problem-search" placeholder="Search by question, topic or platform…" value="${escapeHtml(f.q)}"><select class="filter-select" id="difficulty-filter"><option>All</option>${['Easy','Medium','Hard'].map(x=>`<option ${f.difficulty===x?'selected':''}>${x}</option>`).join('')}</select><select class="filter-select" id="pattern-filter"><option value="All">All patterns</option>${patterns.items.map(x=>`<option value="${escapeHtml(x.name)}" ${f.pattern===x.name?'selected':''}>${escapeHtml(x.name)}</option>`).join('')}</select><select class="filter-select" id="platform-filter"><option>All</option>${platforms.items.map(x=>`<option value="${escapeHtml(x)}" ${f.platform===x?'selected':''}>${escapeHtml(x)}</option>`).join('')}</select><select class="filter-select" id="status-filter"><option value="All">Any status</option><option value="todo" ${f.status==='todo'?'selected':''}>To do</option><option value="in_progress" ${f.status==='in_progress'?'selected':''}>In progress</option><option value="solved" ${f.status==='solved'?'selected':''}>Solved</option></select></div>
  <div class="table-wrap"><table class="problem-table"><thead><tr><th style="width:110px">Status</th><th>Problem</th><th style="width:95px">Difficulty</th><th style="width:185px">Primary pattern</th><th style="width:110px">Practice</th></tr></thead><tbody>${rows || `<tr><td colspan="5"><div class="empty-state"><b>No matching problems</b>Try removing a filter or searching for a different topic.</div></td></tr>`}</tbody></table></div>
  <div class="mobile-problem-list">${mobile || `<div class="empty-state"><b>No matching problems</b>Try removing a filter.</div>`}</div>
  <div class="pagination"><span>Showing ${start}–${end} of ${data.total}</span><div style="display:flex;gap:7px"><button class="btn" data-page="prev" ${f.page===0?'disabled':''}>← Previous</button><button class="btn" data-page="next" ${end>=data.total?'disabled':''}>Next →</button></div></div>
  <p class="analysis-note">Catalogue entries store third-party metadata and official links only. Original statements, examples and official test suites remain with their source platforms.</p>`;
}

async function patternsView() {
  const data = await api('/api/patterns'); state.patterns = data.items;
  const descriptions = {
    'Hash Map':'Use key-value lookups to count, pair or index values efficiently.', 'Hash Set':'Track membership to avoid repeated scans.', 'Two Pointers':'Move two indices with an invariant instead of checking every pair.', 'Sliding Window':'Maintain a dynamic contiguous range as the input moves.', 'Binary Search':'Use an ordered or monotonic search space to cut work logarithmically.', 'Dynamic Programming':'Reuse answers to overlapping subproblems through states and transitions.', 'Tree DFS':'Explore a tree recursively while carrying state up or down.', 'Graph Traversal':'Visit graph nodes safely with BFS, DFS and visited tracking.', 'Stack':'Use last-in-first-out order for parsing and next-greater patterns.', 'Greedy':'Make a local choice supported by a correctness argument.', 'Prefix Sum':'Precompute cumulative values for fast range queries.', 'Monotonic Stack':'Maintain an ordered stack to resolve next/previous greater or smaller values.',
  };
  return `<div class="page-heading"><div><div class="eyebrow">THINK IN REUSABLE TOOLS</div><h1>DSA patterns</h1><p>Recognise the shape of a problem before choosing the data structure or algorithm.</p></div><button class="btn primary" data-nav="problems">Practise a pattern ↗</button></div>
  <div class="grid pattern-grid">${data.items.map((p,i)=>`<article class="pattern-card" data-pattern="${escapeHtml(p.name)}"><div class="card-top"><div class="pattern-icon">${['⌕','↔','▱','⌘','⌁','◈'][i%6]}</div><span class="pill">${p.count} questions</span></div><h3>${escapeHtml(p.name)}</h3><p>${escapeHtml(descriptions[p.name] || `Build fluency in ${p.name.toLowerCase()} through progressively harder problems.`)}</p><div class="pattern-bottom"><span>Easy → Medium → Hard</span><b>Explore ↗</b></div></article>`).join('')}</div>`;
}

async function roadmapView() {
  const data = await api('/api/roadmaps');
  const statusLabels = { complete: 'Completed', 'in-progress': 'In progress', ready: 'Ready', locked: 'Prerequisites first', 'catalogue-gap': 'Catalogue gap' };
  const cards = data.items.map((path, index) => {
    const modules = path.modules.map((module, moduleIndex) => {
      const questions = module.recommended.length
        ? `<div class="path-question-list">${module.recommended.map(problem => `<button class="path-question" data-open-problem="${escapeHtml(problem.slug)}"><span><b>${escapeHtml(problem.title)}</b><small>${escapeHtml(problem.pattern)} · ${escapeHtml(problem.platform)}</small></span><em class="difficulty-${problem.difficulty.toLowerCase()}">${escapeHtml(problem.difficulty)}</em><span aria-hidden="true">↗</span></button>`).join('')}</div>`
        : `<p class="path-empty">${module.total_problems ? 'You have completed the currently available questions in this module.' : 'No matching catalogue questions yet. This module is defined, but its problem coverage needs to be added.'}</p>`;
      const prerequisiteText = module.prerequisites.length ? `<small class="path-prereq">Prerequisites: ${module.prerequisites.map(id => escapeHtml(path.modules.find(x=>x.id===id)?.title || id)).join(', ')}</small>` : '';
      return `<article class="path-module ${module.status}"><div class="path-module-index">${String(moduleIndex+1).padStart(2,'0')}</div><div class="path-module-main"><div class="path-module-top"><h4>${escapeHtml(module.title)}</h4><span class="path-state ${module.status}">${statusLabels[module.status]}</span></div><p>${escapeHtml(module.objective)}</p><div class="path-meter"><span style="width:${module.progress_pct}%"></span></div><div class="path-metrics"><span>${module.solved}/${module.target_count} target solved</span><span>${module.total_problems} in catalogue</span><span>${module.minutes} min</span></div>${prerequisiteText}${questions}</div></article>`;
    }).join('');
    return `<article class="roadmap-card path-card"><div class="path-card-head"><div><div class="eyebrow">TRACK 0${index+1} · ${escapeHtml(path.level)}</div><h3>${escapeHtml(path.name)}</h3><p>${escapeHtml(path.description)}</p><small class="path-outcome">Outcome: ${escapeHtml(path.outcome)}</small></div><div class="path-card-meta"><span class="pill">${escapeHtml(path.duration)}</span><strong>${path.progress_pct}%</strong><small>${path.solved}/${path.target_count} target solves</small></div></div><div class="path-overall-meter"><span style="width:${path.progress_pct}%"></span></div><div class="path-card-stats"><span>${path.completed_modules}/${path.module_count} modules complete</span><span>${path.modules.reduce((n,m)=>n+m.total_problems,0)} catalogue matches</span></div><div class="path-modules">${modules}</div></article>`;
  }).join('');
  return `<div class="page-heading"><div><div class="eyebrow">A SEQUENCE, NOT A CHECKLIST</div><h1>Learning paths</h1><p>Progressive, catalogue-backed DSA tracks. Every module links to actual questions and updates as you record completions.</p></div><div class="heading-actions"><span class="pill violet">${data.items.length} tracks</span><button class="btn primary" data-nav="problems">Browse all problems ↗</button></div></div><div class="path-note"><b>${data.personalised ? 'Progress is personalised' : 'Preview mode'}</b><span>${escapeHtml(data.progress_basis)}. A completed module requires solving the module target available in the current catalogue; prerequisites unlock at 60% mastery.</span></div><div class="roadmap-list">${cards}</div>`;
}

function playgroundView() {
  return `<div class="page-heading"><div><div class="eyebrow">WRITE · RUN · LEARN</div><h1>Code playground</h1><p>Run C, C++, Java and Python in an isolated Judge0 execution environment.</p></div><span class="pill violet">4 languages</span></div>
  <div class="panel" style="padding:0;overflow:hidden"><div class="editor-toolbar"><div class="editor-toolbar-left"><span class="editor-label">SCRATCH.JS</span><select class="lang-select" id="language-select">${Object.entries(languageNames).map(([k,v])=>`<option value="${k}" ${state.editorLanguage===k?'selected':''}>${v}</option>`).join('')}</select></div><div class="editor-toolbar-right"><button class="btn small" data-action="reset-code">Reset</button><button class="btn small primary" data-action="run-code">Run code ▶</button></div></div><div class="editor-container" id="editor-container"><textarea class="code-fallback" id="code-fallback" spellcheck="false" aria-label="Source code">${escapeHtml(templates[state.editorLanguage])}</textarea></div><div class="console"><div class="console-head"><span class="console-title">Execution console</span><span class="pill" id="run-status">Idle</span></div><div class="console-body"><textarea class="stdin-area" id="stdin-input" placeholder="Custom input (stdin)" aria-label="Program input"></textarea><pre class="output-box" id="output-box"><span class="placeholder">Run your program to see stdout, errors, execution time and memory usage here.</span></pre></div></div><div class="run-footer"><small>Sandboxed execution · CPU 2s · Memory 128 MB · Network restricted by Judge0 configuration</small><small>Auto-save is local to this browser</small></div></div>
  <div class="analysis-note">A successful run means the program executed without a runtime or compilation error. It is not an Accepted problem verdict because this scratchpad has no official problem test suite attached.</div>`;
}

async function renderProblem(slug) {
  const p = await api(`/api/problems/${encodeURIComponent(slug)}`); state.currentProblem = p;
  document.title = `${p.title} — AlgoForge`;
  const native = !!p.is_native;
  if (!p.function_mode_supported) state.editorMode = 'stdin';
  const examples = (p.examples || []).map((ex, i) => `<article class="example-card"><div class="example-title">Example ${i+1}</div><div class="example-io"><div><b>Input</b><pre>${escapeHtml(ex.input)}</pre></div><div><b>Output</b><pre>${escapeHtml(ex.output)}</pre></div></div></article>`).join('');
  const hints = (p.hints || []).map((hint, i) => `<details class="hint-item"><summary>Reveal hint ${i+1}</summary><p>${escapeHtml(hint)}</p></details>`).join('');
  const statement = native
    ? `<div class="eyebrow">ALGOFORGE ORIGINAL · PROBLEM STATEMENT</div><h2 class="detail-title">${escapeHtml(p.title)}</h2><div class="statement-text">${escapeHtml(p.description || '')}</div>${p.constraints ? `<div class="constraint-box"><b>Constraints</b><p>${escapeHtml(p.constraints)}</p></div>` : ''}${examples ? `<h4 class="statement-section-title">Examples</h4>${examples}` : ''}${hints ? `<h4 class="statement-section-title">Hints</h4>${hints}` : ''}<div class="source-callout"><b>Platform-owned judging</b><p>This original problem has private test cases. Submit your code to receive an Accepted or failed-test verdict. Hidden inputs and expected outputs are never sent to the browser.</p></div>`
    : `<div class="eyebrow">THIRD-PARTY PROBLEM METADATA</div><h2 class="detail-title">${escapeHtml(p.title)}</h2><div class="detail-copy"><p>This catalogue entry points to the original problem on <b>${escapeHtml(p.platform)}</b>. AlgoForge stores title, source, difficulty and topic metadata only. The original statement, examples, editorials and hidden tests stay with the source platform.</p><h4>What to focus on</h4><p>Primary pattern: <code>${escapeHtml(p.pattern)}</code></p><p>Related topics: ${(p.topics||[]).map(x=>`<code>${escapeHtml(x)}</code>`).join(' ')}</p><h4>Target complexity</h4><p>Time: <code>${escapeHtml(p.time_complexity || 'Not verified')}</code><br>Space: <code>${escapeHtml(p.space_complexity || 'Not verified')}</code></p><p>Open the source problem to read the full statement and constraints. Then use the workspace to run a standalone program with custom input.</p></div><div class="source-callout"><b>Source and attribution</b><p>${escapeHtml(p.platform)} · Metadata-only record · No third-party statement or test cases are hosted here.</p><a class="table-link" href="${escapeHtml(p.url)}" target="_blank" rel="noopener noreferrer">View original problem ↗</a></div><div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap"><button class="btn small" data-action="progress" data-status="in_progress" data-slug="${p.slug}">Mark in progress</button><button class="btn small primary" data-action="progress" data-status="solved" data-slug="${p.slug}">Mark solved externally</button></div><p class="analysis-note">External completion is self-reported, not verified by ${escapeHtml(p.platform)}.</p>`;
  const sampleInput = native && p.examples?.length ? p.examples[0].input : '';
  const contestPill = state.activeContestSlug ? `<span class="pill violet">Contest submission mode</span>` : '';
  const detail = `<div class="workspace-top"><div><div class="workspace-title">${escapeHtml(p.title)}</div><div class="workspace-meta"><span class="pill ${p.difficulty.toLowerCase()}">${p.difficulty}</span><span class="pill">${escapeHtml(p.pattern)}</span><span class="pill">${escapeHtml(p.platform)}</span>${contestPill}</div></div><div class="heading-actions">${!native ? `<a class="btn small" href="${escapeHtml(p.url)}" target="_blank" rel="noopener noreferrer">Original problem ↗</a>` : ''}<button class="btn small" data-action="bookmark" data-slug="${p.slug}">${p.bookmarked?'★ Saved':'☆ Save'}</button></div></div>
  <div class="workspace-grid"><section class="problem-detail"><div class="detail-tabs"><button class="detail-tab active" data-detail-tab="overview">${native?'Statement':'Overview'}</button><button class="detail-tab" data-detail-tab="notes">My notes</button><button class="detail-tab" data-detail-tab="complexity">Complexity</button><button class="detail-tab" data-detail-tab="discussions">Discussions</button></div><div id="detail-tab-content">${statement}</div></section>
  <div class="workspace-splitter" role="separator" aria-label="Resize problem and editor panels" tabindex="0"></div>
  <section class="editor-card"><div class="editor-toolbar"><div class="editor-toolbar-left"><span class="editor-label">SOLUTION</span><select class="lang-select" id="language-select">${Object.entries(languageNames).map(([k,v])=>`<option value="${k}" ${state.editorLanguage===k?'selected':''}>${v}</option>`).join('')}</select>${native && p.function_mode_supported ? `<select class="lang-select" id="editor-mode-select" aria-label="Execution mode"><option value="stdin" ${state.editorMode==='stdin'?'selected':''}>Standard I/O</option><option value="function" ${state.editorMode==='function'?'selected':''}>Function-based</option></select>` : ''}</div><div class="editor-toolbar-right"><span id="editor-save-status" class="save-state">${state.user ? 'Synced draft' : 'Local draft'}</span><button class="btn small" data-action="show-versions">History</button><button class="btn small" data-action="reset-code">Reset</button>${native ? '<button class="btn small" data-action="run-custom-tests">Run tests ▶</button><button class="btn small primary" data-action="submit-solution">Submit ✓</button>' : '<button class="btn small primary" data-action="run-code">Run code ▶</button>'}</div></div><div id="version-history-panel" class="version-history-panel" hidden></div><div class="editor-container" id="editor-container"><textarea class="code-fallback" id="code-fallback" spellcheck="false" aria-label="Source code"></textarea></div><div class="editor-footer"><span id="editor-language-label">${languageNames[state.editorLanguage]} · ${state.editorMode==='function'?'Function':'Standard I/O'} mode</span><span>Ctrl / Cmd + Enter to run tests · Autosave on</span></div><div class="console"><div class="console-head"><div class="console-tabs"><button class="console-tab active" data-output-tab="output">Test results</button><button class="console-tab" data-output-tab="complexity">Complexity</button></div><span class="pill" id="run-status">Idle</span></div>${native ? `<div class="custom-test-toolbar"><b>Custom test cases</b><span>Optional expected output enables comparison</span><button class="btn small" data-action="add-test-case">+ Add case</button></div><div id="custom-test-cases" class="custom-test-cases"><div class="custom-test-row"><label>Input<textarea data-case-input>${escapeHtml(sampleInput)}</textarea></label><label>Expected output<textarea data-case-expected>${escapeHtml(p.examples?.[0]?.output || '')}</textarea></label></div></div>` : `<div class="console-body"><textarea class="stdin-area" id="stdin-input" placeholder="Custom input (stdin)" aria-label="Program input">${escapeHtml(sampleInput)}</textarea></div>`}<div class="output-results output-box" id="output-box"><span class="placeholder">${native ? 'Run custom cases or submit against the full private test suite.' : 'Run your code to see output here.'}</span></div></div><div class="run-footer"><small>${native ? 'Platform-owned test-suite judging · CPU 2s · Memory 128 MB' : 'Custom-input run only · 2s CPU · 128 MB memory'}</small><small>Autosave and version history ${state.user ? 'sync to your account' : 'are stored in this browser'}</small></div></section></div>`;
  document.getElementById('app-root').innerHTML = renderShell(detail, 'problem', 'Problem workspace');
  mountResizablePanels();
  mountEditor(slug, 'problem');
  loadNote(slug);
}

function mountResizablePanels() {
  const grid = document.querySelector('.workspace-grid');
  const handle = grid?.querySelector('.workspace-splitter');
  if (!grid || !handle) return;
  const min = 28, max = 64;
  const initial = Number(localStorage.getItem('algoforge-workspace-detail-width')) || 40;
  const applyWidth = value => {
    const width = Math.max(min, Math.min(max, value));
    grid.style.setProperty('--detail-width', `${width}%`);
    handle.setAttribute('aria-valuemin', String(min));
    handle.setAttribute('aria-valuemax', String(max));
    handle.setAttribute('aria-valuenow', String(Math.round(width)));
    return width;
  };
  applyWidth(initial);
  let active = false;
  const move = event => {
    if (!active) return;
    const rect = grid.getBoundingClientRect();
    applyWidth(((event.clientX - rect.left) / rect.width) * 100);
  };
  const stop = () => {
    if (!active) return;
    active = false;
    document.body.classList.remove('resizing-panels');
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', stop);
    window.removeEventListener('pointercancel', stop);
    const width = parseFloat(getComputedStyle(grid).getPropertyValue('--detail-width')) || 40;
    localStorage.setItem('algoforge-workspace-detail-width', String(width));
  };
  handle.addEventListener('pointerdown', event => {
    if (window.innerWidth <= 820) return;
    event.preventDefault();
    active = true;
    document.body.classList.add('resizing-panels');
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', stop);
    window.addEventListener('pointercancel', stop);
  });
  handle.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const current = parseFloat(getComputedStyle(grid).getPropertyValue('--detail-width')) || 40;
    const next = event.key === 'Home' ? min : event.key === 'End' ? max : current + (event.key === 'ArrowRight' ? 2 : -2);
    const width = applyWidth(next);
    localStorage.setItem('algoforge-workspace-detail-width', String(width));
  });
}

async function loadNote(slug) {
  if (!state.user) return;
  try {
    const note = await api(`/api/problems/${slug}/note`);
    state.problemNote = note.content;
  } catch { state.problemNote = ''; }
}

async function submissionsView() {
  if (!state.user) return `<div class="page-heading"><div><div class="eyebrow">YOUR HISTORY</div><h1>Submissions</h1><p>Sign in to keep a record of code runs.</p></div></div><div class="empty-state"><b>Sign in to see submission history</b><button class="btn primary" data-action="login" style="margin-top:10px">Sign in</button></div>`;
  const data = await api('/api/submissions');
  return `<div class="page-heading"><div><div class="eyebrow">EXECUTION HISTORY</div><h1>Submissions</h1><p>Every saved code run, including runtime and memory measurements.</p></div><button class="btn primary" data-nav="playground">Open playground ↗</button></div><div class="table-wrap"><table class="problem-table"><thead><tr><th>ID</th><th>Language</th><th>Result</th><th>Execution time</th><th>Memory</th><th>Submitted</th></tr></thead><tbody>${data.items.map(s=>`<tr><td class="mono">#${s.id}</td><td>${languageNames[s.language]||s.language}</td><td><span class="status-dot ${s.status==='Executed'?'solved':''}">${escapeHtml(s.status)}</span></td><td class="mono">${s.time_seconds ? `${escapeHtml(s.time_seconds)}s`:'—'}</td><td class="mono">${s.memory_kb ? `${s.memory_kb} KB`:'—'}</td><td>${new Date(s.created_at).toLocaleString()}</td></tr>`).join('') || `<tr><td colspan="6"><div class="empty-state"><b>No submissions yet</b>Run your first program in the playground.</div></td></tr>`}</tbody></table></div><p class="analysis-note">“Executed” means Judge0 ran the program successfully. It does not mean a problem-specific test suite accepted the solution.</p>`;
}

async function contestsView() {
  const data = await api('/api/contests');
  return `<div class="page-heading"><div><div class="eyebrow">TIMED PRACTICE</div><h1>Contests</h1><p>Scheduled contests with server-side start windows, registration, judged submissions and a scored leaderboard.</p></div><span class="pill violet">${data.items.length} published</span></div><div class="contest-list">${data.items.map(c => `<article class="contest-card"><div class="contest-card-main"><div class="contest-card-top"><span class="pill ${c.status==='live'?'easy':c.status==='upcoming'?'violet':'default'}">${escapeHtml(c.status)}</span><span class="muted">${c.participants} registered · ${c.problems} problems</span></div><h3>${escapeHtml(c.title)}</h3><p>${escapeHtml(c.description)}</p><div class="contest-date">${new Date(c.starts_at).toLocaleString()} – ${new Date(c.ends_at).toLocaleString()}</div></div><button class="btn primary" data-contest-open="${escapeHtml(c.slug)}">View contest ↗</button></article>`).join('') || `<div class="empty-state"><b>No scheduled contests yet</b>When an administrator publishes a contest, registration, problem access and scoring will appear here.</div>`}</div><div class="panel" style="margin-top:14px"><b>Practice while you wait</b><p class="analysis-note">You can create a timed, self-guided practice session from the problem library. Scheduled contests are scored only on AlgoForge-original problems with platform-owned test cases.</p><button class="btn" data-nav="problems">Browse practice problems ↗</button></div>`;
}

async function contestDetailView(slug) {
  const [contest, board] = await Promise.all([api(`/api/contests/${encodeURIComponent(slug)}`), api(`/api/contests/${encodeURIComponent(slug)}/leaderboard`)]);
  const problems = contest.problems.map((p,i)=>`<div class="contest-problem-row"><div><b>${i+1}. ${escapeHtml(p.title)}</b><div class="problem-sub">${escapeHtml(p.difficulty)} · ${escapeHtml(p.pattern)} · ${p.points} points</div></div><button class="btn small" data-contest-problem="${escapeHtml(p.slug)}" ${contest.status==='upcoming'?'disabled':''}>Open problem</button></div>`).join('');
  const leaderboard = board.items.map(row=>`<tr><td>${row.rank}</td><td>${escapeHtml(row.display_name)}</td><td>${row.score}</td><td>${row.solved}</td><td>${row.penalty_minutes} min</td></tr>`).join('');
  return `<div class="page-heading"><div><div class="eyebrow">${escapeHtml(contest.status.toUpperCase())} CONTEST</div><h1>${escapeHtml(contest.title)}</h1><p>${escapeHtml(contest.description)}</p></div><button class="btn" data-nav="contests">← All contests</button></div><div class="grid stats-grid"><div class="stat-card"><div class="stat-top">Status</div><div class="stat-value" style="font-size:19px">${escapeHtml(contest.status)}</div></div><div class="stat-card"><div class="stat-top">Problems</div><div class="stat-value">${contest.problem_count}</div></div><div class="stat-card"><div class="stat-top">Start</div><div class="stat-value" style="font-size:14px">${new Date(contest.starts_at).toLocaleString()}</div></div><div class="stat-card"><div class="stat-top">End</div><div class="stat-value" style="font-size:14px">${new Date(contest.ends_at).toLocaleString()}</div></div></div>${!contest.registered ? `<div class="panel contest-register"><div><b>Join the contest</b><p class="analysis-note">Register before the contest ends. Problems unlock for registered participants at the scheduled start time.</p></div><button class="btn primary" data-contest-register="${escapeHtml(slug)}">Register now</button></div>` : `<div class="panel"><b>You are registered</b><p class="analysis-note">${contest.status==='upcoming'?'Problem statements unlock at the start time.':'Your submissions are eligible for the official AlgoForge leaderboard while the contest is live.'}</p></div>`}<div class="grid contest-detail-grid"><section class="panel"><div class="panel-title">Contest problems</div>${problems || `<div class="empty-state">${contest.status==='upcoming'?'Problems are hidden until the start time.':'Register for this contest to access its problems.'}</div>`}</section><section class="panel"><div class="panel-title">Leaderboard</div><div class="table-wrap"><table class="problem-table"><thead><tr><th>Rank</th><th>Student</th><th>Points</th><th>Solved</th><th>Penalty</th></tr></thead><tbody>${leaderboard || '<tr><td colspan="5">No accepted submissions yet.</td></tr>'}</tbody></table></div></section></div>`;
}

async function bookmarksView() {
  if (!state.user) return `<div class="page-heading"><div><div class="eyebrow">YOUR COLLECTION</div><h1>Saved questions</h1><p>Sign in to keep a personal revision list.</p></div></div><div class="empty-state"><b>Save questions for later</b><button class="btn primary" data-action="login" style="margin-top:10px">Sign in</button></div>`;
  const data = await api('/api/problems?bookmarked=true&limit=100');
  return `<div class="page-heading"><div><div class="eyebrow">YOUR COLLECTION</div><h1>Saved questions</h1><p>Questions you want to revisit or solve later.</p></div><button class="btn primary" data-nav="problems">Find more questions ↗</button></div><div class="mobile-problem-list" style="display:grid">${data.items.map(p=>`<article class="mobile-problem" data-open-problem="${p.slug}"><div class="mobile-problem-top"><h3>${escapeHtml(p.title)}</h3><span class="pill ${p.difficulty.toLowerCase()}">${p.difficulty}</span></div><div class="mobile-problem-meta"><span class="pattern-tag">${escapeHtml(p.pattern)}</span><span class="muted">${escapeHtml(p.platform)}</span></div></article>`).join('') || `<div class="empty-state"><b>No saved questions yet</b>Use the star button on a problem to add it here.</div>`}</div>`;
}

async function profileView() {
  if (!state.user) return `<div class="empty-state"><b>Sign in to view your profile</b><button class="btn primary" data-action="login">Sign in</button></div>`;
  const [d, achievements] = await Promise.all([api('/api/dashboard'), api('/api/achievements')]);
  const badges = achievements.items.map(a=>`<article class="achievement-card ${a.unlocked?'unlocked':'locked'}"><div class="achievement-icon">${a.unlocked?'◆':'◇'}</div><div><b>${escapeHtml(a.title)}</b><p>${escapeHtml(a.description)}</p></div><span>${a.unlocked?'Unlocked':'Locked'}</span></article>`).join('');
  return `<div class="page-heading"><div><div class="eyebrow">YOUR LEARNING RECORD</div><h1>Progress & profile</h1><p>Manage your learning profile, review achievements and inspect your practice consistency.</p></div></div><div class="panel profile-header"><div class="avatar" style="width:48px;height:48px;font-size:15px">${userInitials()}</div><div><b>${escapeHtml(state.user.display_name)}</b><div class="muted">${escapeHtml(state.user.email)}</div></div><span class="pill violet">${escapeHtml(state.user.role)}</span></div><div class="grid stats-grid"><div class="stat-card"><div class="stat-top">Solved</div><div class="stat-value">${d.solved}</div><div class="stat-foot">Of ${d.total_questions} catalogue entries</div></div><div class="stat-card"><div class="stat-top">Current streak</div><div class="stat-value">${d.streak} days</div><div class="stat-foot">Longest: ${d.longest_streak} days</div></div><div class="stat-card"><div class="stat-top">Easy</div><div class="stat-value">${d.easy}</div><div class="stat-foot">Fundamentals</div></div><div class="stat-card"><div class="stat-top">Medium / Hard</div><div class="stat-value">${d.medium} / ${d.hard}</div><div class="stat-foot">Deeper reasoning</div></div></div><section class="panel"><div class="panel-title">Profile settings</div><form id="profile-form" class="profile-form"><label class="field"><span>Display name</span><input name="display_name" required minlength="2" maxlength="80" value="${escapeHtml(state.user.display_name)}"></label><label class="field"><span>Timezone</span><input name="timezone" required value="${escapeHtml(state.user.timezone || 'Asia/Kolkata')}" placeholder="Asia/Kolkata"></label><button class="btn primary" type="submit">Save profile</button></form></section><section class="panel" style="margin-top:14px"><div class="panel-title">Achievements</div><div class="achievement-grid">${badges}</div></section><section class="panel" style="margin-top:14px"><div class="panel-title">Data and account controls</div><p class="analysis-note">External platform completions are self-reported. AlgoForge-original problems are marked solved only after the backend judge accepts all private test cases. You can delete your account and associated progress, notes, bookmarks, sessions, contest registrations and submissions.</p><button class="btn small danger" data-action="delete-account" style="margin-top:12px">Delete my account</button></section>`;
}

async function adminView() {
  if (!state.user || state.user.role !== 'admin') return `<div class="empty-state"><b>Admin access required</b>This page is available only to an account configured with the admin role.</div>`;
  const [d, problems, reports] = await Promise.all([api('/api/admin/summary'), api('/api/admin/problems'), api('/api/admin/discussion-reports')]);
  const problemOptions = problems.items.map(p=>`<option value="${escapeHtml(p.slug)}">${escapeHtml(p.title)}</option>`).join('');
  const reportRows = reports.items.map(r=>`<article class="moderation-row"><div><b>${escapeHtml(r.discussion_title)}</b><p>${escapeHtml(r.reason)}</p><small>${escapeHtml(r.reporter)} · ${new Date(r.created_at).toLocaleString()}</small></div><div><button class="btn small danger" data-action="moderate-discussion" data-discussion-id="${r.discussion_id}" data-hide="true">Hide</button><button class="btn small" data-action="moderate-discussion" data-discussion-id="${r.discussion_id}" data-hide="false">Keep visible</button></div></article>`).join('');
  return `<div class="page-heading"><div><div class="eyebrow">PLATFORM OPERATIONS</div><h1>Admin console</h1><p>Manage original judged problems and publish scheduled contests.</p></div></div><div class="grid stats-grid"><div class="stat-card"><div class="stat-top">Users</div><div class="stat-value">${d.users}</div></div><div class="stat-card"><div class="stat-top">Problems</div><div class="stat-value">${d.problems}</div></div><div class="stat-card"><div class="stat-top">Submissions</div><div class="stat-value">${d.submissions}</div></div><div class="stat-card"><div class="stat-top">Pending reports</div><div class="stat-value">${d.pending_reports || 0}</div></div><div class="stat-card"><div class="stat-top">Judge service</div><div class="stat-value" style="font-size:17px">${d.judge_configured?'Configured':'Not configured'}</div></div></div><div class="admin-grid"><section class="panel"><div class="panel-title">Create a contest</div><p class="analysis-note">Use timezone-aware start and end times. Only AlgoForge-original problems with judge test cases can be selected.</p><form id="contest-create-form"><label class="field"><span>Contest title</span><input name="title" required minlength="3" maxlength="180" placeholder="Weekly DSA Challenge"></label><label class="field"><span>URL slug</span><input name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="weekly-dsa-challenge"></label><label class="field"><span>Description</span><textarea name="description" maxlength="3000" placeholder="Contest details"></textarea></label><div class="form-two"><label class="field"><span>Starts</span><input name="starts_at" type="datetime-local" required></label><label class="field"><span>Ends</span><input name="ends_at" type="datetime-local" required></label></div><label class="field"><span>Problems (Ctrl/Cmd-click to select multiple)</span><select name="problem_slugs" multiple required size="7">${problemOptions}</select></label><button class="btn primary" type="submit">Publish contest</button></form></section><section class="panel"><div class="panel-title">Original problem catalogue</div><p class="analysis-note">${problems.items.length} platform-owned problems with test-case judging. Add new tasks through the protected admin API, including a statement, sample and hidden cases.</p><div class="admin-problem-list">${problems.items.map(p=>`<div><b>${escapeHtml(p.title)}</b><span>${escapeHtml(p.slug)} · ${escapeHtml(p.difficulty)} · ${p.test_cases} tests · ${escapeHtml(p.pattern)}</span></div>`).join('')}</div><details class="admin-api-help"><summary>Problem authoring API payload and JSON editor</summary><p>Create, update or delete original judged problems. Updates are blocked after a problem has submissions, and deletion is blocked while progress, submissions or contests reference it.</p><form id="admin-problem-form"><label class="field"><span>Operation</span><select name="operation"><option value="create">Create</option><option value="update">Update</option><option value="delete">Delete</option></select></label><label class="field"><span>Problem slug</span><input name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="my-new-problem"></label><label class="field"><span>Full problem JSON (not needed for delete)</span><textarea name="payload" rows="12" spellcheck="false">{
  "slug": "my-new-problem",
  "title": "My New Problem",
  "difficulty": "Easy",
  "pattern": "Arrays",
  "topics": ["Arrays"],
  "description": "Read an integer n and print n.\\n\\nInput: one integer.\\nOutput: print the same integer.",
  "constraints": "0 <= n <= 1000000",
  "time_complexity": "O(1)",
  "space_complexity": "O(1)",
  "hints": ["Read the value and print it."],
  "test_cases": [
    {"input": "4\\n", "output": "4\\n", "sample": true},
    {"input": "9\\n", "output": "9\\n", "sample": false}
  ]
}</textarea></label><button class="btn primary" type="submit">Apply problem operation</button></form></details></section></div><div class="panel" style="margin-top:14px"><div class="panel-title">Community moderation</div><p class="analysis-note">${reports.items.length} unresolved reports. Hidden discussions are no longer visible to learners; moderation actions resolve the linked reports.</p>${reportRows || '<div class="empty-state">No pending discussion reports.</div>'}</div><div class="panel" style="margin-top:14px"><b>Question catalogue import</b><p class="analysis-note">The third-party catalogue is metadata-only and points to original official sources. Run <code>python scripts/import_codeforces.py</code> from a machine with internet access to expand it toward the 150 Easy / 250 Medium / 100 Hard target.</p></div>`;
}

function notFoundView() {
  return `<div class="empty-state" style="margin:60px auto;max-width:460px"><div class="eyebrow">404 · ROUTE NOT FOUND</div><b style="font-size:21px">This path doesn't exist.</b>The page may have moved or the link may be incorrect.<div style="margin-top:15px"><button class="btn primary" data-nav="dashboard">Return to overview</button></div></div>`;
}

function renderAuth(page) {
  state.authMode = page === 'register' ? 'register' : 'login';
  document.title = `${page==='register'?'Create account':'Sign in'} — AlgoForge`;
  const isRegister = state.authMode === 'register';
  document.getElementById('app-root').innerHTML = `<div class="auth-screen"><div class="auth-top-actions">${themeToggleButton()}<button class="btn auth-home" data-nav="welcome" type="button">Home</button></div><section class="auth-art"><div>${brandIdentity()}<div class="auth-art-copy"><div class="eyebrow">A PRACTICE SPACE BUILT AROUND HOW YOU THINK</div><h1>Build the habit.<br><em>Understand the pattern.</em></h1><p>Work through focused DSA practice, write code in your preferred language and keep a clear record of what you have learned.</p></div></div><div class="auth-art-bottom"><span class="auth-art-line"></span><div class="quote">Less random grinding. More deliberate practice.</div></div></section><section class="auth-side" id="main-content"><form class="auth-card" id="auth-form"><div class="eyebrow">${isRegister?'CREATE YOUR ACCOUNT':'YOUR WORKSPACE'}</div><h2>${isRegister?'Start practising with purpose':'Welcome back'}</h2><p>${isRegister?'Save your notes, bookmarks and learning history.':'Your next focused session starts here.'}</p>${isRegister?`<div class="field"><label for="display-name">Display name</label><input id="display-name" name="display_name" autocomplete="name" minlength="2" maxlength="80" required placeholder="Your name"></div>`:''}<div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" required placeholder="you@example.com"></div><div class="field"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="${isRegister?'new-password':'current-password'}" minlength="${isRegister?10:1}" required placeholder="${isRegister?'At least 10 characters':'Your password'}"></div><div class="auth-error" id="auth-error"></div><button class="btn primary" type="submit">${isRegister?'Create account':'Sign in'} <span aria-hidden="true">→</span></button>${!isRegister?`<button type="button" class="btn" data-action="demo-login" style="width:100%;margin-top:8px">Use local demo account</button>`:''}<div class="auth-switch">${isRegister?'Already have an account?':'New to AlgoForge?'} <button type="button" class="text-button" data-action="auth-switch">${isRegister?'Sign in':'Create an account'}</button></div><div class="auth-switch"><a href="#/privacy">Privacy</a> · <a href="#/terms">Terms</a></div></form></section></div>`;
}

function renderLanding() {
  document.title = 'AlgoForge — DSA practice, with a plan';
  document.getElementById('app-root').innerHTML = `<div class="public-home">
    <header class="site-header">
      ${brandIdentity(true)}
      <nav class="public-nav-links" aria-label="Main navigation"><a href="#features" data-scroll="features">What you can do</a><a href="#/problems">Problem library</a><a href="#/roadmap">Learning paths</a></nav>
      <div class="public-nav-actions">${themeToggleButton()}<button class="btn nav-signin" data-action="login">Sign in</button></div>
    </header>
    <main id="main-content">
      <section class="hero hero-premium">
        <div class="hero-copy">
          <div class="hero-kicker"><span class="kicker-mark">AF</span><span>DSA PRACTICE · PATTERN FIRST</span></div>
          <h1>Understand the pattern.<br><em>Own the solution.</em></h1>
          <p class="hero-lede">A focused place to practise data structures and algorithms. Find the right problem, work through it in your language, and see where your problem-solving is improving.</p>
          <div class="hero-actions"><button class="btn primary hero-primary" data-nav="problems">Explore problems <span aria-hidden="true">↗</span></button><button class="btn hero-secondary" data-nav="roadmap">View learning paths</button></div>
          <div class="hero-meta"><span><i class="meta-dot"></i> Pattern-based practice</span><span><i class="meta-dot"></i> C · C++ · Java · Python</span><span><i class="meta-dot"></i> Personal progress history</span></div>
        </div>
        <div class="hero-stage-wrap">
          <div class="stage-caption"><span>INSIDE THE WORKSPACE</span><span>PROBLEM → CODE → FEEDBACK</span></div>
          <div class="hero-stage" aria-label="Illustrative preview of the AlgoForge coding workspace">
            <div class="stage-topbar"><div class="stage-brand"><span class="stage-brand-mark">A</span><span>algoforge <small>/ practice</small></span></div><span class="stage-window-label">WORKSPACE PREVIEW</span></div>
            <div class="stage-content">
              <section class="stage-problem"><div class="stage-problem-overline"><span>ARRAYS · HASH MAP</span><span class="stage-difficulty">EASY</span></div><h2>Two Sum</h2><p>Find the indices of two numbers that add up to a target.</p><div class="stage-example"><small>EXAMPLE</small><code>nums = [2, 7, 11, 15]<br>target = 9</code><div class="stage-output"><span>OUTPUT</span><b>[0, 1]</b></div></div><div class="stage-problem-foot"><span>01 / PROBLEM STATEMENT</span><span>Constraints & examples</span></div></section>
              <section class="stage-editor"><div class="editor-mini-toolbar"><span class="editor-language"><i></i> C++</span><span>main.cpp <b>⌄</b></span><span class="editor-mini-run">Run</span></div><pre class="editor-code"><span class="code-muted">01</span> <span class="code-keyword">class</span> <span class="code-type">Solution</span> {<br><span class="code-muted">02</span>   <span class="code-keyword">public:</span><br><span class="code-muted">03</span>   vector&lt;<span class="code-type">int</span>&gt; twoSum( ) {<br><span class="code-muted">04</span>     unordered_map&lt;int,int&gt; seen;<br><span class="code-muted">05</span>     <span class="code-comment">// work through the pattern</span><br><span class="code-muted">06</span>   }<br><span class="code-muted">07</span> };</pre><div class="editor-mini-footer"><span><i></i> Ready to run</span><span>Lines 7 · C++17</span></div></section>
            </div>
            <div class="stage-bottom"><span><b>01</b> Read the problem</span><span><b>02</b> Write your approach</span><span><b>03</b> Learn from the result</span></div>
          </div>
          <p class="stage-disclaimer">Illustrative interface preview · not a live submission</p>
        </div>
      </section>
      <section class="intro-rail"><span class="intro-rail-label">THE PRACTICE LOOP</span><p>Know what to practise. Understand <em>why it works.</em> Measure what gets better.</p><a href="#features" data-scroll="features">See how it works <span aria-hidden="true">↓</span></a></section>
      <section class="feature-band feature-band-premium" id="features"><div class="section-intro"><div><div class="eyebrow">BUILT FOR CONSISTENT PRACTICE</div><h2>Everything has a place.<br><em>Your progress has a direction.</em></h2></div><p>Not another endless list of questions. AlgoForge connects problem patterns, a practical coding space and your learning history.</p></div><div class="feature-grid premium-feature-grid">
        <article class="feature-tile premium-feature"><span class="feature-index">01</span><div class="feature-symbol">⌗</div><h3>Find the pattern</h3><p>Explore problems by topic, difficulty and technique. Build familiarity with the ideas that appear again and again.</p><a href="#/problems">Browse the problem library <span>↗</span></a></article>
        <article class="feature-tile premium-feature"><span class="feature-index">02</span><div class="feature-symbol">{ }</div><h3>Work through the solution</h3><p>Use a dedicated editor for C, C++, Java and Python. Run examples, test your own inputs and review submissions.</p><a href="#/playground">Open the playground <span>↗</span></a></article>
        <article class="feature-tile premium-feature"><span class="feature-index">03</span><div class="feature-symbol">↗</div><h3>See your progress</h3><p>Track practice activity, revisit weaker patterns and use weekly feedback to decide what to work on next.</p><a href="#/analytics">Explore learning analytics <span>↗</span></a></article>
      </div></section>
      <section class="method-section"><div class="method-heading"><div class="eyebrow">A SIMPLE WAY TO GET BETTER</div><h2>One problem at a time.<br><em>With intention.</em></h2></div><div class="method-steps"><div><span>01</span><b>Choose a focus</b><p>Start with a pattern or follow a structured learning path.</p></div><div><span>02</span><b>Attempt it yourself</b><p>Write, run and refine your approach before looking for help.</p></div><div><span>03</span><b>Review and repeat</b><p>Use complexity feedback and activity history to guide the next session.</p></div></div></section>
    </main>
    <footer class="site-footer site-footer-premium"><span>© ${new Date().getFullYear()} AlgoForge · An independent DSA practice workspace</span><span><a href="#/privacy">Privacy</a><a href="#/terms">Terms</a><a href="#/problems">Problem library</a></span></footer>
  </div>`;
  syncThemeControls();
}

function renderPolicy(page) {
  const privacy = page === 'privacy';
  document.title = `${privacy?'Privacy Policy':'Terms & Conditions'} — AlgoForge`;
  const content = privacy ? `<h1>Privacy Policy</h1><p><strong>Draft notice:</strong> This policy is a project template and must be reviewed and completed by the operator before public launch. The operator's legal identity, contact details, hosting location and retention periods are not yet configured.</p><p>Last updated: October 30, 2026.</p><h2>Information this application may process</h2><p>When you create an account, AlgoForge stores your email address, display name and a salted password hash. When you use the practice features, it may store your progress status, bookmarks, notes, discussions, replies, votes, reports, source code submitted to the execution service, execution results and timestamps. Public discussion posts and replies may be visible to other users until removed or moderated. The application does not intentionally request precise location, contacts, camera or microphone access.</p><h2>Code execution and third parties</h2><p>Source code and standard input you choose to run are sent to the configured Judge0 service. The operator must identify its hosting provider, configure retention and access controls, and publish the relevant subprocessors before launch. Do not submit credentials or confidential code.</p><h2>Cookies and local storage</h2><p>The application uses an HTTP-only session cookie for sign-in. The local cookie-preference banner stores your choice in this browser. Non-essential analytics are disabled by default in this build.</p><h2>Security and retention</h2><p>Passwords are stored as scrypt hashes. Production operators must configure HTTPS, database backups, access controls, a security contact and a documented data-retention schedule. User notes and submissions are retained until deleted under the operator's configured account-deletion process. Account deletion also removes the user's discussions, replies, votes and reports, along with replies and votes attached to discussions the user authored.</p><h2>Your choices</h2><p>Before public launch, add verified processes for access, correction, export and deletion requests, and provide the operator's contact details. This draft is not legal advice and should be reviewed for the jurisdictions in which the service operates.</p>` : `<h1>Terms and Conditions</h1><p><strong>Draft notice:</strong> These terms are a project template, not final legal terms. The operator must add its legal name, contact details, governing law and other required disclosures before inviting public users.</p><p>Last updated: October 30, 2026.</p><h2>Learning service</h2><p>AlgoForge is a study and practice tool. Its question catalogue stores problem metadata and links to third-party platforms. Those platforms control their original problem statements, editorials, hidden tests, submissions, accounts and terms.</p><h2>Acceptable use</h2><p>Do not use the service to upload malicious code, attack infrastructure, bypass execution limits, interfere with other users, post harassment or spam in discussions, disclose another person's private information, or violate applicable laws. The operator may suspend accounts that abuse the service.</p><h2>Code execution</h2><p>Code runs through a separately deployed Judge0 service with configured CPU, memory and time limits. Code execution may be unavailable, delayed or produce environment-dependent measurements. Do not submit secrets, personal data or proprietary source code unless you are authorised to do so.</p><h2>Educational information</h2><p>Complexity estimates are heuristic guidance and are not mathematically guaranteed. Runtime and memory measurements depend on the environment. Externally marked solved problems are self-reported unless an authorised integration verifies the result.</p><h2>Third-party links and intellectual property</h2><p>Links to external platforms are provided for convenience. Their names, content and services belong to their respective owners. AlgoForge is independent and does not imply endorsement or affiliation.</p><h2>Availability and changes</h2><p>The operator may update the service, suspend features or modify these terms. Add the correct liability, warranty, consumer and dispute-resolution clauses after legal review.</p>`;
  document.getElementById('app-root').innerHTML = `<div class="public-home"><header class="site-header">${brandIdentity(true)}<nav class="public-nav-links"><a href="#/welcome">Home</a><a href="#/problems">Problem library</a></nav><div class="public-nav-actions">${themeToggleButton()}<button class="btn primary" data-action="login">Open app</button></div></header><main id="main-content" class="policy-page">${content}<p><a href="#/welcome">← Back to AlgoForge</a></p></main><footer class="site-footer"><span>© ${new Date().getFullYear()} AlgoForge</span><span><a href="#/privacy">Privacy</a> · <a href="#/terms">Terms</a></span></footer></div>`;
}

function showCookieBanner() {
  try { if (localStorage.getItem('algoforge-cookie-choice')) return; } catch (error) { console.warn('Cookie preference is unavailable in this browser context:', error); }
  if (document.querySelector('.cookie-banner')) return;
  const node = document.createElement('div'); node.className = 'cookie-banner';
  node.setAttribute('role', 'region'); node.setAttribute('aria-label', 'Cookie notice');
  node.innerHTML = `<p>AlgoForge uses an essential session cookie to keep you signed in. Optional analytics are not enabled in this build. <a href="#/privacy">Privacy details</a>.</p><div class="cookie-actions"><button class="btn primary" data-cookie="essential">Got it</button></div>`;
  document.body.appendChild(node);
}

function onClick(event) {
  const scrollTarget = event.target.closest('[data-scroll]');
  if (scrollTarget) { event.preventDefault(); document.getElementById(scrollTarget.dataset.scroll)?.scrollIntoView({behavior:'smooth'}); return; }
  const nav = event.target.closest('[data-nav]');
  if (nav) { const r = nav.dataset.nav; setRoute(r); document.getElementById('sidebar')?.classList.remove('open'); return; }
  const open = event.target.closest('[data-open-problem]');
  if (open && open.dataset.openProblem) { setRoute(`problem/${open.dataset.openProblem}`); return; }
  const pattern = event.target.closest('[data-pattern]');
  if (pattern) { state.problems.pattern = pattern.dataset.pattern; state.problems.page = 0; setRoute('problems'); return; }
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action === 'login') { setRoute('login'); }
  else if (action === 'register') { setRoute('register'); }
  else if (action === 'auth-switch') { setRoute(state.authMode === 'login' ? 'register' : 'login'); }
  else if (action === 'demo-login') demoLogin();
  else if (action === 'logout') logout();
  else if (action === 'theme') toggleTheme();
  else if (action === 'mobile-menu') document.getElementById('sidebar')?.classList.toggle('open');
  else if (action === 'retry') renderRoute();
  else if (action === 'run-code') runCode();
  else if (action === 'run-custom-tests') runCustomTests();
  else if (action === 'add-test-case') addCustomTestCase();
  else if (action === 'show-versions') showDraftVersions();
  else if (action === 'submit-solution') submitSolution();
  else if (action === 'reset-code') resetCode();
  else if (action === 'bookmark') bookmarkProblem(event.target.closest('[data-action="bookmark"]').dataset.slug);
  else if (action === 'progress') markProgress(event.target.closest('[data-action="progress"]').dataset.slug, event.target.closest('[data-action="progress"]').dataset.status);
  else if (action === 'start-virtual') startVirtualContest();
  else if (action === 'user-menu') state.user ? setRoute('profile') : setRoute('login');
  else if (action === 'delete-account') deleteAccount();
  else if (action === 'discussion-vote') { const el = event.target.closest('[data-action="discussion-vote"]'); voteDiscussion(Number(el.dataset.discussionId), Number(el.dataset.vote)); }
  else if (action === 'discussion-report') { const el = event.target.closest('[data-action="discussion-report"]'); reportDiscussion(Number(el.dataset.discussionId)); }
  else if (action === 'discussion-delete') { const el = event.target.closest('[data-action="discussion-delete"]'); if (window.confirm('Delete this discussion and its replies?')) api(`/api/discussions/${el.dataset.discussionId}`, { method: 'DELETE' }).then(()=>{toast('Discussion deleted.');refreshDiscussions();}).catch(e=>toast(e.message,'error')); }
  else if (action === 'moderate-discussion') { const el = event.target.closest('[data-action="moderate-discussion"]'); moderateDiscussion(Number(el.dataset.discussionId), el.dataset.hide === 'true'); }
  const restoreVersion = event.target.closest('[data-restore-version]')?.dataset.restoreVersion;
  if (restoreVersion) { restoreDraftVersion(restoreVersion); return; }
  const removeCase = event.target.closest('[data-remove-test-case]');
  if (removeCase) { removeCase.closest('.custom-test-row')?.remove(); return; }
  const contestOpen = event.target.closest('[data-contest-open]')?.dataset.contestOpen;
  if (contestOpen) { state.activeContestSlug = null; setRoute(`contest/${contestOpen}`); return; }
  const contestRegister = event.target.closest('[data-contest-register]')?.dataset.contestRegister;
  if (contestRegister) { registerForContest(contestRegister); return; }
  const contestProblem = event.target.closest('[data-contest-problem]')?.dataset.contestProblem;
  if (contestProblem) { state.activeContestSlug = getRouteDetails().slug; setRoute(`problem/${contestProblem}`); return; }
  const page = event.target.closest('[data-page]')?.dataset.page;
  if (page) { state.problems.page = Math.max(0, state.problems.page + (page === 'next' ? 1 : -1)); renderRoute(); }
  const cookie = event.target.closest('[data-cookie]')?.dataset.cookie;
  if (cookie) { localStorage.setItem('algoforge-cookie-choice', cookie); document.querySelector('.cookie-banner')?.remove(); }
  const tab = event.target.closest('[data-detail-tab]')?.dataset.detailTab;
  if (tab) renderDetailTab(tab);
  const outputTab = event.target.closest('[data-output-tab]')?.dataset.outputTab;
  if (outputTab) { state.outputTab = outputTab; document.querySelectorAll('[data-output-tab]').forEach(x=>x.classList.toggle('active',x.dataset.outputTab===outputTab)); if (outputTab==='complexity' && state.lastComplexity) showComplexity(state.lastComplexity); }
  const step = event.target.closest('[data-roadmap-step]')?.dataset.roadmapStep;
  if (step) { state.problems.q = step; setRoute('problems'); }
}

function onInput(event) {
  if (event.target.id === 'global-search') {
    clearTimeout(state.searchTimer);
    state.searchTimer = setTimeout(() => { state.problems.q = event.target.value; state.problems.page = 0; setRoute('problems'); }, 380);
  }
  if (event.target.id === 'problem-search') {
    clearTimeout(state.filterTimer);
    state.filterTimer = setTimeout(() => { state.problems.q = event.target.value; state.problems.page = 0; renderRoute(); }, 320);
  }
  if ((event.target.id === 'code-fallback' && !state.editor) || event.target.id === 'stdin-input') queueDraftSave();
}
function onChange(event) {
  const id = event.target.id;
  if (['difficulty-filter','pattern-filter','platform-filter','status-filter'].includes(id)) {
    const map = {'difficulty-filter':'difficulty','pattern-filter':'pattern','platform-filter':'platform','status-filter':'status'};
    state.problems[map[id]] = event.target.value; state.problems.page = 0; renderRoute();
  }
  if (id === 'editor-mode-select') {
    state.editorMode=event.target.value;
    if(state.editor){state.editor.dispose();state.editor=null;}
    const container=document.getElementById('editor-container');
    if(container){container.dataset.mounted='0';container.innerHTML='<textarea class="code-fallback" id="code-fallback" spellcheck="false" aria-label="Source code"></textarea>';}
    mountEditor(draftProblemKey(),'problem');
    const label=document.getElementById('editor-language-label');if(label)label.textContent=`${languageNames[state.editorLanguage]} · ${state.editorMode==='function'?'Function':'Standard I/O'} mode`;
  }
  if (id === 'language-select') {
    state.editorLanguage = event.target.value;
    if (state.editor) { state.editor.dispose(); state.editor = null; }
    const container = document.getElementById('editor-container');
    if (container) { container.dataset.mounted = '0'; container.innerHTML = `<textarea class="code-fallback" id="code-fallback" spellcheck="false" aria-label="Source code">${escapeHtml(state.editorMode==='function'?getFunctionTemplate(getRouteDetails().slug, state.editorLanguage):templates[state.editorLanguage])}</textarea>`; }
    const slug = draftProblemKey();
    mountEditor(slug, slug==='playground'?'playground':'problem');
    const label = document.getElementById('editor-language-label'); if(label) label.textContent = `${languageNames[state.editorLanguage]} · Ready`;
  }
}
async function onSubmit(event) {
  if (event.target.id === 'discussion-create-form') {
    event.preventDefault(); const form = new FormData(event.target);
    try { await api(`/api/problems/${encodeURIComponent(state.currentProblem.slug)}/discussions`, { method: 'POST', body: { title: form.get('title'), body: form.get('body') } }); toast('Discussion posted.'); await refreshDiscussions(); }
    catch (error) { toast(error.message, 'error'); if (!state.user) setRoute('login'); }
    return;
  }
  if (event.target.dataset.discussionCommentForm) {
    event.preventDefault(); const discussionId = event.target.dataset.discussionCommentForm; const form = new FormData(event.target);
    try { await api(`/api/discussions/${discussionId}/comments`, { method: 'POST', body: { body: form.get('body') } }); toast('Reply posted.'); await refreshDiscussions(); }
    catch (error) { toast(error.message, 'error'); }
    return;
  }
  if (event.target.id === 'profile-form') {
    event.preventDefault();
    const form = new FormData(event.target);
    try {
      const data = await api('/api/me', { method: 'PUT', body: { display_name: form.get('display_name'), timezone: form.get('timezone') } });
      state.user = data.user; toast('Profile updated.'); renderRoute();
    } catch (error) { toast(error.message, 'error'); }
    return;
  }
  if (event.target.id === 'contest-create-form') {
    event.preventDefault();
    const form = new FormData(event.target);
    const selected = [...event.target.elements.problem_slugs.selectedOptions].map(x => x.value);
    const localToIso = value => new Date(value).toISOString();
    try {
      await api('/api/admin/contests', { method: 'POST', body: { slug: form.get('slug'), title: form.get('title'), description: form.get('description'), starts_at: localToIso(form.get('starts_at')), ends_at: localToIso(form.get('ends_at')), problem_slugs: selected } });
      toast('Contest published.'); setRoute('contests');
    } catch (error) { toast(error.message, 'error'); }
    return;
  }
  if (event.target.id === 'admin-problem-form') {
    event.preventDefault();
    const form = new FormData(event.target);
    const operation = form.get('operation');
    const slug = String(form.get('slug') || '').trim();
    try {
      if (operation === 'delete') {
        if (!window.confirm(`Delete original problem ${slug}? This only works when it has no submissions, contest references or learner progress.`)) return;
        await api(`/api/admin/problems/${encodeURIComponent(slug)}`, { method: 'DELETE' });
        toast('Original problem deleted.');
      } else {
        const payload = JSON.parse(String(form.get('payload') || '{}'));
        if (payload.slug !== slug) throw new Error('The JSON payload slug must match the Problem slug field.');
        await api(operation === 'update' ? `/api/admin/problems/${encodeURIComponent(slug)}` : '/api/admin/problems', { method: operation === 'update' ? 'PUT' : 'POST', body: payload });
        toast(operation === 'update' ? 'Original problem updated.' : 'Original problem created.');
      }
      renderRoute();
    } catch (error) { toast(error.message, 'error'); }
    return;
  }
  if (event.target.id !== 'auth-form') return;
  event.preventDefault();
  const form = new FormData(event.target);
  const isRegister = state.authMode === 'register';
  const body = { email: form.get('email'), password: form.get('password') };
  if (isRegister) { body.display_name = form.get('display_name'); }
  const error = document.getElementById('auth-error'); error.textContent = '';
  try {
    const data = await api(isRegister?'/api/auth/register':'/api/auth/login', { method:'POST', body });
    state.user = data.user; toast(isRegister?'Account created.':'Signed in successfully.'); setRoute('dashboard');
  } catch (e) { error.textContent = e.message; }
}

async function demoLogin() {
  try {
    const data = await api('/api/auth/login', { method:'POST', body:{email:'demo@algoforge.dev',password:'demo-pass-123'} });
    state.user = data.user; toast('Signed in to the local demo account.'); setRoute('dashboard');
  } catch (e) { toast(e.message,'error'); }
}
async function logout() {
  try { await api('/api/auth/logout',{method:'POST'}); } catch {}
  state.user = null; toast('You have signed out.'); setRoute('welcome');
}
function toggleTheme() {
  const nextTheme = document.body.classList.contains('light') ? 'dark' : 'light';
  applyTheme(nextTheme, true);
}
function editorStorageKey() {
  const slug = getRouteDetails().page === 'problem' ? getRouteDetails().slug : 'playground'; return `algoforge-code:${slug}:${state.editorLanguage}:${state.editorMode}`;
}
function draftProblemKey() { const key=getRouteDetails().page === 'problem' ? getRouteDetails().slug : 'playground'; return state.editorMode==='function' && key!=='playground' ? `${key}::function` : key; }
function queueDraftSave() {
  const code=currentCode(), stdin=document.getElementById('stdin-input')?.value || '';
  localStorage.setItem(editorStorageKey(), code);
  const status=document.getElementById('editor-save-status'); if(status) status.textContent='Saving…';
  if(!state.user){if(status)status.textContent='Saved locally';return;}
  clearTimeout(state.draftSaveTimer);
  state.draftSaveTimer=setTimeout(async()=>{
    try { await api(`/api/drafts/${encodeURIComponent(draftProblemKey())}/${state.editorLanguage}`,{method:'PUT',body:{language:state.editorLanguage,source_code:code,stdin}}); if(status)status.textContent='All changes saved'; }
    catch(error){if(status)status.textContent='Local backup only';console.warn('Draft sync failed:',error);}
  },900);
}
async function saveDraftNow() {
  queueDraftSave(); if(!state.user)return;
  clearTimeout(state.draftSaveTimer);
  const code=currentCode(),stdin=document.getElementById('stdin-input')?.value||'';
  await api(`/api/drafts/${encodeURIComponent(draftProblemKey())}/${state.editorLanguage}`,{method:'PUT',body:{language:state.editorLanguage,source_code:code,stdin}});
  const status=document.getElementById('editor-save-status');if(status)status.textContent='All changes saved';
}
async function showDraftVersions() {
  const panel=document.getElementById('version-history-panel');if(!panel)return;
  panel.hidden=false;panel.innerHTML='<span class="muted">Loading saved versions…</span>';
  if(!state.user){panel.innerHTML='<span class="muted">Sign in to keep version history across devices. Local autosave is active.</span>';return;}
  try{const data=await api(`/api/drafts/${encodeURIComponent(draftProblemKey())}/${state.editorLanguage}/versions`);panel.innerHTML=data.items.length?data.items.map(v=>`<div class="version-row"><span><b>${new Date(v.created_at).toLocaleString()}</b><small>${escapeHtml(v.preview||'Empty draft')}</small></span><button class="btn small" data-restore-version="${v.id}">Restore</button></div>`).join(''):'<span class="muted">No previous versions yet. Change the code to create a snapshot.</span>';}
  catch(error){panel.textContent=error.message;}
}
async function restoreDraftVersion(versionId) {
  try{const result=await api(`/api/drafts/${encodeURIComponent(draftProblemKey())}/${state.editorLanguage}/restore`,{method:'POST',body:{version_id:Number(versionId)}});setCode(result.source_code);const stdin=document.getElementById('stdin-input');if(stdin)stdin.value=result.stdin;localStorage.setItem(editorStorageKey(),result.source_code);toast('Code version restored.');queueDraftSave();const panel=document.getElementById('version-history-panel');if(panel)panel.hidden=true;}
  catch(error){toast(error.message,'error');}
}
function currentCode() {
  if (state.editor) return state.editor.getValue();
  return document.getElementById('code-fallback')?.value ?? templates[state.editorLanguage];
}
function setCode(value) {
  if (state.editor) state.editor.setValue(value);
  else if (document.getElementById('code-fallback')) document.getElementById('code-fallback').value = value;
}
function resetCode() { setCode(state.editorMode==='function' ? getFunctionTemplate(getRouteDetails().slug, state.editorLanguage) : templates[state.editorLanguage]); localStorage.removeItem(editorStorageKey()); queueDraftSave(); toast('Starter template restored.'); }

async function mountEditor(slug, mode) {
  const container = document.getElementById('editor-container'); if (!container) return;
  const key = editorStorageKey();
  let saved = localStorage.getItem(key) || (state.editorMode==='function' ? getFunctionTemplate(getRouteDetails().slug, state.editorLanguage) : templates[state.editorLanguage]);
  if(state.user){try{const remote=await api(`/api/drafts/${encodeURIComponent(draftProblemKey())}/${state.editorLanguage}`);if(remote.draft){saved=remote.draft.source_code;localStorage.setItem(key,saved);const stdin=document.getElementById('stdin-input');if(stdin)stdin.value=remote.draft.stdin||stdin.value;}}catch{}}
  const saveStatus=document.getElementById('editor-save-status');if(saveStatus)saveStatus.textContent=state.user?'Synced draft':'Saved locally';
  const fallback = document.getElementById('code-fallback'); if (fallback) fallback.value = saved;
  // Monaco is loaded lazily. The textarea remains a working fallback if the CDN is blocked.
  if (!window.require) {
    try { await loadScript('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs/loader.min.js'); } catch { return; }
  }
  if (!window.require || !container.isConnected) return;
  window.MonacoEnvironment = { getWorkerUrl: function() { return `data:text/javascript;charset=utf-8,${encodeURIComponent("self.MonacoEnvironment={baseUrl:'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/'};importScripts('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs/base/worker/workerMain.js');")}`; } };
  window.require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs' } });
  window.require(['vs/editor/editor.main'], function() {
    if (!container.isConnected || container.dataset.mounted === '1') return;
    container.dataset.mounted = '1'; container.innerHTML = '';
    state.editor = monaco.editor.create(container, {
      value: saved,
      language: state.editorLanguage,
      theme: document.body.classList.contains('light')?'vs':'vs-dark',
      automaticLayout: true,
      minimap: { enabled: false },
      fontSize: 12,
      fontFamily: 'DM Mono, Consolas, monospace',
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      tabSize: 4,
      wordWrap: 'on',
      padding: { top: 12, bottom: 12 },
      roundedSelection: false,
      glyphMargin: false,
      folding: true,
      suggestOnTriggerCharacters: true,
    });
    state.editor.onDidChangeModelContent(() => queueDraftSave());
    state.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => getRouteDetails().page === 'problem' && state.currentProblem?.is_native ? runCustomTests() : runCode());
  });
}
function loadScript(src) {
  return new Promise((resolve,reject)=>{
    const existing = [...document.scripts].find(s=>s.src===src);
    if (existing) { existing.addEventListener('load',resolve,{once:true}); existing.addEventListener('error',reject,{once:true}); if (window.require) resolve(); return; }
    const script = document.createElement('script'); script.src=src; script.async=true; script.onload=resolve; script.onerror=reject; document.head.appendChild(script);
  });
}

async function runCode() {
  const code = currentCode();
  const stdin = document.getElementById('stdin-input')?.value || '';
  const box = document.getElementById('output-box'); const badge = document.getElementById('run-status');
  if (!code.trim()) { toast('Write some code before running.','error'); return; }
  if (badge) badge.textContent = 'Queued';
  if (box) box.textContent = 'Sending code to the isolated execution service…';
  const runButton = document.querySelector('[data-action="run-code"]'); if(runButton){runButton.disabled=true;runButton.textContent='Running…';}
  try {
    const slug = getRouteDetails().page === 'problem' ? state.currentProblem?.slug : null;
    const result = await api('/api/run',{method:'POST',body:{language:state.editorLanguage,source_code:code,stdin,problem_slug:slug}});
    state.lastComplexity = result.complexity;
    if (badge) badge.textContent = result.status;
    if (box) box.textContent = 'Execution queued. Waiting for compiler…';
    await pollRun(result.id, 0, result.access_token);
  } catch (e) {
    if (box) box.textContent = e.message;
    if (badge) badge.textContent = 'Unavailable';
    toast(e.message,'error');
  } finally {
    const btn = document.querySelector('[data-action="run-code"]'); if(btn){btn.disabled=false;btn.innerHTML='Run ▶';}
  }
}
async function pollRun(id, attempt, accessToken) {
  if (attempt > 25) { document.getElementById('output-box').textContent = 'Execution is taking longer than expected. Open Submissions to check the saved run.'; return; }
  await new Promise(r=>setTimeout(r,900));
  try {
    const result = await api(`/api/run/${id}`, { headers: accessToken ? { 'X-Run-Token': accessToken } : {} });
    const badge = document.getElementById('run-status'); if (badge) badge.textContent = result.status;
    if (['Queued','In Queue','Processing','Compiling'].includes(result.status)) return pollRun(id,attempt+1,accessToken);
    const output = [result.stdout ? `STDOUT\n${result.stdout}`:'', result.compile_output ? `COMPILE OUTPUT\n${result.compile_output}`:'', result.stderr ? `STDERR\n${result.stderr}`:''].filter(Boolean).join('\n\n') || '(Program finished with no output)';
    const box = document.getElementById('output-box'); if (box) box.textContent = output;
    state.lastComplexity = result.complexity;
    state.lastRunMetrics = result;
    if (state.outputTab === 'complexity') showComplexity(result.complexity);
    if (result.status === 'Executed') toast(`Program executed · ${result.time_seconds || '—'}s · ${result.memory_kb || '—'} KB`);
    else toast(`Execution ended: ${result.status}`,'error');
  } catch (e) { document.getElementById('output-box').textContent = e.message; }
}
function showComplexity(data) {
  const box = document.getElementById('output-box'); if (!box || !data) return;
  const m = state.lastRunMetrics || {};
  box.innerHTML = `<div class="complexity-strip"><div class="complexity-box"><span>Estimated time</span><b>${escapeHtml(data.estimated_time||'Unknown')}</b></div><div class="complexity-box"><span>Expected time</span><b>${escapeHtml(data.expected_time||'Not verified')}</b></div><div class="complexity-box"><span>Estimated space</span><b>${escapeHtml(data.estimated_space||'Unknown')}</b></div><div class="complexity-box"><span>Expected space</span><b>${escapeHtml(data.expected_space||'Not verified')}</b></div></div><div class="complexity-box" style="margin-top:8px"><span>Measured execution</span><b>${m.time_seconds?escapeHtml(m.time_seconds)+'s':'Not available'} · ${m.memory_kb?escapeHtml(m.memory_kb)+' KB':'Not available'}</b></div><p class="analysis-note">${(data.caveats||[]).map(escapeHtml).join(' ')}</p>`;
}

async function bookmarkProblem(slug) {
  try { const result = await api(`/api/problems/${slug}/bookmark`,{method:'POST'}); toast(result.bookmarked?'Added to saved questions.':'Removed from saved questions.'); renderRoute(); }
  catch(e){toast(e.message,'error'); if(!state.user)setRoute('login');}
}
async function markProgress(slug,status) {
  try { const result = await api(`/api/problems/${slug}/progress`,{method:'POST',body:{status}}); toast(result.note || `Marked ${status.replace('_',' ')}.`); if(result.note) toast('This completion is self-reported, not verified by the source platform.',''); renderRoute(); }
  catch(e){toast(e.message,'error'); if(!state.user)setRoute('login');}
}
function renderDetailTab(tab) {
  document.querySelectorAll('[data-detail-tab]').forEach(x=>x.classList.toggle('active',x.dataset.detailTab===tab));
  const target = document.getElementById('detail-tab-content'); if(!target || !state.currentProblem) return;
  if (tab==='notes') {
    const note = state.problemNote || '';
    target.innerHTML = `<div class="eyebrow">PERSONAL REVISION</div><h3 style="font-size:14px">Your notes</h3><p class="analysis-note">Notes are private to your account. Sign in to save them across sessions.</p><textarea class="note-area" id="problem-note" placeholder="Record the key insight, edge cases or a mistake to avoid…">${escapeHtml(note)}</textarea><div style="display:flex;justify-content:flex-end;margin-top:9px"><button class="btn primary small" data-action="save-note">Save notes</button></div>`;
  } else if (tab==='complexity') {
    target.innerHTML = `<div class="eyebrow">COMPLEXITY REFERENCE</div><h3 style="font-size:14px">Expected algorithmic cost</h3><div class="complexity-strip"><div class="complexity-box"><span>Target time</span><b>${escapeHtml(state.currentProblem.time_complexity||'Not verified')}</b></div><div class="complexity-box"><span>Target space</span><b>${escapeHtml(state.currentProblem.space_complexity||'Not verified')}</b></div></div><p class="analysis-note">Run your code to see a heuristic source estimate and measured runtime/memory. The estimate is not a formal proof of Big-O complexity.</p>`;
  } else if (tab==='discussions') {
    target.innerHTML = `<div class="eyebrow">COMMUNITY KNOWLEDGE</div><h3 style="font-size:14px">Discuss this problem</h3><p class="analysis-note">Share an approach, ask about an edge case or explain a useful invariant. Keep solutions and explanations respectful and spoiler-aware.</p><div class="discussion-loading">Loading discussions…</div>`;
    loadDiscussions(state.currentProblem.slug, target);
  } else {
    const p = state.currentProblem;
    target.innerHTML = `<div class="eyebrow">PROBLEM METADATA</div><h2 class="detail-title">${escapeHtml(p.title)}</h2><div class="detail-copy"><p>This catalogue entry points to the original problem on <b>${escapeHtml(p.platform)}</b>. AlgoForge stores the title, source, difficulty and topic metadata; the original statement, sample examples, editorials and hidden tests stay on the source platform.</p><h4>What to focus on</h4><p>Primary pattern: <code>${escapeHtml(p.pattern)}</code></p><p>Related topics: ${(p.topics||[]).map(x=>`<code>${escapeHtml(x)}</code>`).join(' ')}</p><h4>Target complexity</h4><p>Time: <code>${escapeHtml(p.time_complexity||'Not verified')}</code><br>Space: <code>${escapeHtml(p.space_complexity||'Not verified')}</code></p><p>Open the source problem to read the full statement and constraints. Then use the workspace to write and run a standalone program with custom input.</p></div><div class="source-callout"><b>Source and attribution</b><p>${escapeHtml(p.platform)} · Metadata-only import · No third-party statement or test cases are hosted here.</p><a class="table-link" href="${escapeHtml(p.url)}" target="_blank" rel="noopener noreferrer">View original problem ↗</a></div><div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap"><button class="btn small" data-action="progress" data-status="in_progress" data-slug="${p.slug}">Mark in progress</button><button class="btn small primary" data-action="progress" data-status="solved" data-slug="${p.slug}">Mark solved externally</button></div><p class="analysis-note">“Mark solved externally” is a self-reported completion, not an authenticated verdict from ${escapeHtml(p.platform)}.</p></div>`;
  }
}
async function loadDiscussions(slug, target) {
  if (!target || !target.isConnected) return;
  try {
    const data = await api(`/api/problems/${encodeURIComponent(slug)}/discussions`);
    const createForm = state.user ? `<form id="discussion-create-form" class="discussion-compose"><label class="field"><span>Discussion title</span><input name="title" minlength="5" maxlength="180" required placeholder="What did you find challenging?"></label><label class="field"><span>Your question or explanation</span><textarea name="body" rows="3" minlength="10" maxlength="8000" required placeholder="Explain your approach, intuition or edge case…"></textarea></label><button class="btn primary small" type="submit">Post discussion</button></form>` : `<div class="discussion-signin"><span>Sign in to start a discussion or reply.</span><button class="btn small primary" data-action="login">Sign in</button></div>`;
    const posts = data.items.map(item => `<article class="discussion-card"><div class="discussion-heading"><div><b>${escapeHtml(item.title)}</b><div class="discussion-meta">${escapeHtml(item.author)} · ${new Date(item.created_at).toLocaleString()} ${item.is_hidden ? '· Hidden' : ''}</div></div><div class="discussion-votes"><button class="vote-btn ${item.my_vote===1?'active':''}" data-action="discussion-vote" data-discussion-id="${item.id}" data-vote="1" aria-label="Upvote discussion">▲</button><b>${item.score}</b><button class="vote-btn ${item.my_vote===-1?'active':''}" data-action="discussion-vote" data-discussion-id="${item.id}" data-vote="-1" aria-label="Downvote discussion">▼</button></div></div><p class="discussion-body">${escapeHtml(item.body)}</p><div class="discussion-replies">${item.comments.map(comment=>`<div class="discussion-comment"><b>${escapeHtml(comment.author)}</b><span>${escapeHtml(comment.body)}</span><small>${new Date(comment.created_at).toLocaleString()}</small></div>`).join('') || '<p class="analysis-note">No replies yet.</p>'}</div>${state.user ? `<form class="discussion-reply-form" data-discussion-comment-form="${item.id}"><textarea name="body" rows="2" minlength="2" maxlength="4000" required placeholder="Write a helpful reply…"></textarea><div class="discussion-actions"><button class="btn small" type="submit">Reply</button>${!item.is_owner ? `<button class="text-button" type="button" data-action="discussion-report" data-discussion-id="${item.id}">Report</button>` : ''}${item.is_owner || state.user.role==='admin' ? `<button class="text-button danger-text" type="button" data-action="discussion-delete" data-discussion-id="${item.id}">Delete</button>` : ''}${state.user.role==='admin' ? `<button class="text-button" type="button" data-action="moderate-discussion" data-discussion-id="${item.id}" data-hide="${!item.is_hidden}">${item.is_hidden?'Unhide':'Hide'}</button>` : ''}</div></form>` : ''}</article>`).join('');
    target.innerHTML = `<div class="discussion-feed">${createForm}${posts || '<div class="empty-state"><b>No discussions yet</b>Start a thread about the reasoning, complexity or edge cases.</div>'}</div>`;
  } catch (error) { target.innerHTML = `<div class="empty-state"><b>Could not load discussions</b>${escapeHtml(error.message)}</div>`; }
}

async function refreshDiscussions() {
  const target = document.getElementById('detail-tab-content');
  if (target && state.currentProblem) await loadDiscussions(state.currentProblem.slug, target);
}

async function voteDiscussion(id, value) {
  try { await api(`/api/discussions/${id}/vote`, { method: 'POST', body: { value } }); await refreshDiscussions(); }
  catch (error) { toast(error.message, 'error'); if (!state.user) setRoute('login'); }
}

async function reportDiscussion(id) {
  const reason = window.prompt('Why should a moderator review this discussion?');
  if (!reason) return;
  try { await api(`/api/discussions/${id}/report`, { method: 'POST', body: { reason } }); toast('Report sent to moderators.'); }
  catch (error) { toast(error.message, 'error'); }
}

async function moderateDiscussion(id, isHidden) {
  try { await api(`/api/admin/discussions/${id}/moderate`, { method: 'POST', body: { is_hidden: isHidden } }); toast(isHidden ? 'Discussion hidden and reports resolved.' : 'Discussion made visible and reports resolved.'); renderRoute(); }
  catch (error) { toast(error.message, 'error'); }
}

async function saveNote() {
  const slug = state.currentProblem?.slug; if(!slug) return;
  const content = document.getElementById('problem-note')?.value || '';
  try { await api(`/api/problems/${slug}/note`,{method:'PUT',body:{content}}); state.problemNote=content; toast('Notes saved.'); }
  catch(e){toast(e.message,'error');if(!state.user)setRoute('login');}
}

async function deleteAccount() {
  if (!state.user) return;
  if (!window.confirm('Delete your AlgoForge account and associated progress, notes, bookmarks, submissions and community activity? Discussions you authored and their replies will also be deleted. This cannot be undone.')) return;
  try { await api('/api/account',{method:'DELETE'}); state.user=null; toast('Account and associated data deleted.'); setRoute('welcome'); }
  catch(e) { toast(e.message,'error'); }
}

async function registerForContest(slug) {
  if (!state.user) { toast('Sign in before registering for a contest.', 'error'); setRoute('login'); return; }
  try { await api(`/api/contests/${encodeURIComponent(slug)}/register`, { method: 'POST' }); toast('Contest registration confirmed.'); renderRoute(); }
  catch (error) { toast(error.message, 'error'); }
}

function addCustomTestCase() {
  const host=document.getElementById('custom-test-cases');if(!host)return;
  const row=document.createElement('div');row.className='custom-test-row';
  row.innerHTML='<label>Input<textarea data-case-input placeholder="Example input"></textarea></label><label>Expected output<textarea data-case-expected placeholder="Optional expected output"></textarea></label><button class="btn small danger" type="button" data-remove-test-case>Remove</button>';
  host.appendChild(row);
}
async function runCustomTests() {
  if(!state.user){toast('Sign in to run custom tests.','error');setRoute('login');return;}
  const problem=state.currentProblem;if(!problem?.is_native)return;
  const cases=[...document.querySelectorAll('.custom-test-row')].map(row=>({input:row.querySelector('[data-case-input]')?.value||'',expected_output:row.querySelector('[data-case-expected]')?.value??''}));
  if(!cases.length||cases.some(row=>!row.input.trim())){toast('Add input for every custom test case.','error');return;}
  const box=document.getElementById('output-box'),badge=document.getElementById('run-status'),button=document.querySelector('[data-action="run-custom-tests"]');
  if(button){button.disabled=true;button.textContent='Running…';}if(badge)badge.textContent='Running';if(box)box.textContent='Running your custom cases in the isolated judge…';
  try{const result=await api(`/api/problems/${encodeURIComponent(problem.slug)}/run-custom`,{method:'POST',body:{language:state.editorLanguage,source_code:currentCode(),mode:state.editorMode,test_cases:cases}});await pollCustomSubmission(result.id,0);}
  catch(error){if(box)box.textContent=error.message;if(badge)badge.textContent='Unavailable';toast(error.message,'error');}
  finally{const btn=document.querySelector('[data-action="run-custom-tests"]');if(btn){btn.disabled=false;btn.textContent='Run tests ▶';}}
}
async function pollCustomSubmission(id,attempt){
  if(attempt>35)return;
  await new Promise(resolve=>setTimeout(resolve,850));
  const result=await api(`/api/submissions/${id}/judge`);const badge=document.getElementById('run-status');if(badge)badge.textContent=result.status;
  if(result.status==='Judging'||result.status==='Running Custom Tests')return pollCustomSubmission(id,attempt+1);
  state.lastComplexity=result.complexity;state.lastRunMetrics=result;
  const box=document.getElementById('output-box');
  if(box)box.innerHTML=`<div class="result-summary"><b>${escapeHtml(result.status)}</b><span>${result.passed}/${result.compared_total ?? result.total} comparisons passed${result.execution_only_total ? ` · ${result.execution_only_total} execution-only` : ''}</span><small>Complexity: ${escapeHtml(result.complexity?.estimated_time||'Unknown')} time · ${escapeHtml(result.complexity?.estimated_space||'Unknown')} space</small></div><div class="case-result-list">${(result.cases||[]).map(row=>`<article class="case-result ${row.passed===true?'pass':row.passed===false?'fail':'executed'}"><div class="case-result-head"><b>Test case ${row.case}</b><span>${escapeHtml(row.status)}${row.has_expected_output?'':' · execution only'}</span><small>${row.time_seconds?escapeHtml(row.time_seconds)+'s':'—'} · ${row.memory_kb?escapeHtml(row.memory_kb)+' KB':'—'}</small></div><div class="case-output"><small>Program output</small><pre>${escapeHtml(row.stdout||'(no output)')}</pre></div>${row.expected_output?`<div class="case-output"><small>Expected output</small><pre>${escapeHtml(row.expected_output)}</pre></div>`:''}${row.compile_output||row.stderr?`<div class="case-output error"><small>Diagnostics</small><pre>${escapeHtml(row.compile_output||row.stderr)}</pre></div>`:''}</article>`).join('')}</div>`;
  toast(result.status==='Custom Tests Passed'?'All custom tests passed.':result.status==='Executed'?'Executed; add expected outputs for comparisons.':`Custom test result: ${result.status}`,result.status==='Custom Tests Passed'||result.status==='Executed'?'success':'error');
}

async function submitSolution() {
  if (!state.user) { toast('Sign in to submit a judged solution.', 'error'); setRoute('login'); return; }
  const problem = state.currentProblem;
  if (!problem?.is_native) { toast('Only AlgoForge-original problems have platform-owned judging.', 'error'); return; }
  const button = document.querySelector('[data-action="submit-solution"]');
  const badge = document.getElementById('run-status'); const box = document.getElementById('output-box');
  if (button) { button.disabled = true; button.textContent = 'Submitting…'; }
  if (badge) badge.textContent = 'Judging';
  if (box) box.textContent = 'Submitting your source code to the private test suite…';
  try {
    const data = await api(`/api/problems/${encodeURIComponent(problem.slug)}/submit`, { method: 'POST', body: { language: state.editorLanguage, source_code: currentCode(), contest_slug: state.activeContestSlug || null, mode: state.editorMode } });
    await pollJudgedSubmission(data.id, 0);
  } catch (error) {
    if (box) box.textContent = error.message;
    if (badge) badge.textContent = 'Unavailable';
    toast(error.message, 'error');
  } finally {
    const btn = document.querySelector('[data-action="submit-solution"]'); if (btn) { btn.disabled = false; btn.textContent = 'Submit ✓'; }
  }
}

async function pollJudgedSubmission(id, attempt) {
  const badge = document.getElementById('run-status'); const box = document.getElementById('output-box');
  if (attempt > 40) { if (box) box.textContent = `Submission #${id} is still being judged. Open Submissions to inspect it later.`; return; }
  await new Promise(resolve => setTimeout(resolve, 900));
  const result = await api(`/api/submissions/${id}/judge`);
  if (badge) badge.textContent = result.status;
  if (result.status === 'Judging') {
    if (box) box.textContent = `Judging private test cases… ${result.passed}/${result.total} passed`;
    return pollJudgedSubmission(id, attempt + 1);
  }
  state.lastComplexity = result.complexity; state.lastRunMetrics = result;
  if (box) box.innerHTML = `<div class="result-summary"><b>${escapeHtml(result.status)}</b><span>${result.passed}/${result.total} private cases passed</span><small>Complexity estimate: ${escapeHtml(result.complexity?.estimated_time || 'Unknown')} time · ${escapeHtml(result.complexity?.estimated_space || 'Unknown')} space</small></div><div class="case-result-list">${(result.cases || []).map(row => `<article class="case-result ${row.passed ? 'pass' : 'fail'}"><div class="case-result-head"><b>Test case ${row.case}</b><span>${escapeHtml(row.status)}</span><small>${row.time_seconds ? `${escapeHtml(row.time_seconds)}s` : '—'} · ${row.memory_kb ? `${escapeHtml(row.memory_kb)} KB` : '—'}</small></div>${row.stdout ? `<div class="case-output"><small>Public sample output</small><pre>${escapeHtml(row.stdout)}</pre></div>` : ''}${row.compile_output || row.stderr ? `<div class="case-output error"><small>Diagnostics</small><pre>${escapeHtml(row.compile_output || row.stderr)}</pre></div>` : ''}</article>`).join('')}</div>`;
  if (result.status === 'Accepted') { toast('Accepted — all private test cases passed.'); state.activeContestSlug = null; }
  else toast(`Submission result: ${result.status}`, 'error');
  if (state.outputTab === 'complexity') showComplexity(result.complexity);
}

async function startVirtualContest() {
  const difficulty = document.getElementById('contest-difficulty').value;
  const length = document.getElementById('contest-length').value;
  try {
    const data = await api(`/api/problems?difficulty=${difficulty}&limit=8`);
    const panel = document.getElementById('virtual-contest-result');
    panel.innerHTML = `<div class="panel"><div class="panel-head"><div><div class="panel-title">Your ${length}-minute practice set</div><div class="panel-subtitle">${data.items.length} problems · ${difficulty} · timer not enforced by server</div></div><span class="pill violet">Virtual session</span></div>${data.items.map((p,i)=>`<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-top:1px solid var(--border)"><div><b style="font-size:11px">${i+1}. ${escapeHtml(p.title)}</b><div class="problem-sub">${escapeHtml(p.pattern)}</div></div><button class="btn small" data-open-problem="${p.slug}">Open ↗</button></div>`).join('') || '<div class="empty-state">No questions at this difficulty yet. Import the expanded catalogue.</div>'}</div>`;
  } catch(e) { toast(e.message,'error'); }
}

// Save-note action has its own path so it cannot be mistaken for global navigation.
document.addEventListener('click', event => {
  if (event.target.closest('[data-action="save-note"]')) saveNote();
});


// The application script is loaded with defer in production; invoke the SPA bootstrap explicitly.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true });
} else {
  init();
}
