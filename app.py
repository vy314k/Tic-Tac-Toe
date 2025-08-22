# app.py — Single-file Flask Tic-Tac-Toe (Fully functional Vs Computer: Easy/Normal/Unbeatable)
from flask import Flask, request, jsonify, render_template_string
import random
from typing import List, Tuple, Optional

app = Flask(__name__)

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

# ---------- Game utilities ----------
def check_winner(board: List[str]) -> Tuple[Optional[str], List[int]]:
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], [a, b, c]
    if all(cell for cell in board):
        return 'Draw', []
    return None, []

# Minimax with alpha-beta and move ordering to speed up
def minimax(board: List[str], depth: int, is_max: bool, ai_sym: str, human_sym: str,
            alpha: int = -10**9, beta: int = 10**9) -> Tuple[int, Optional[int]]:
    winner, _ = check_winner(board)
    if winner == ai_sym:
        return 10 - depth, None
    if winner == human_sym:
        return depth - 10, None
    if winner == 'Draw':
        return 0, None

    # Move ordering: center, corners, sides
    order = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    best_move = None
    if is_max:
        best_score = -10**9
        for i in order:
            if not board[i]:
                board[i] = ai_sym
                score, _ = minimax(board, depth + 1, False, ai_sym, human_sym, alpha, beta)
                board[i] = ''
                if score > best_score:
                    best_score = score
                    best_move = i
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        return best_score, best_move
    else:
        best_score = 10**9
        for i in order:
            if not board[i]:
                board[i] = human_sym
                score, _ = minimax(board, depth + 1, True, ai_sym, human_sym, alpha, beta)
                board[i] = ''
                if score < best_score:
                    best_score = score
                    best_move = i
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
        return best_score, best_move

# ---------- Flask endpoints ----------
@app.route('/')
def index():
    # Single-file front-end (HTML + CSS + JS) — improved grid + robust client logic
    return render_template_string("""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Tic-Tac-Toe — Flask (AI fixed)</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f4f7fb; --card:#fff; --muted:#6b7280; --border:#e6eef8;
  --accent-x:#ff4d6d; --accent-o:#3b82f6; --win:#dff7dd;
}
*{box-sizing:border-box;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial;}
body{margin:0;background:linear-gradient(180deg,#f7f9fc 0%, #eef4ff 100%);color:#0f172a;}
.wrap{max-width:1100px;margin:28px auto;padding:20px;}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;}
h1{font-size:20px;margin:0}
.layout{display:grid;grid-template-columns:320px 1fr;gap:20px;}
.card{background:var(--card);border-radius:12px;padding:16px;box-shadow:0 8px 30px rgba(12,18,36,0.06);}
.controls label{display:block;color:var(--muted);font-size:13px;margin-top:12px}
select, button{margin-top:8px;padding:8px 10px;border-radius:8px;border:1px solid #e6eef8;background:#fff}
.btn{background:#111827;color:#fff;border:none;padding:10px 12px;border-radius:10px;cursor:pointer}
.btn.alt{background:#fff;border:1px solid #e6eef8;color:var(--muted)}
.top-actions{display:flex;gap:8px;align-items:center}
.board-wrap{display:flex;flex-direction:column;align-items:center;padding:18px}
.board{
  --cell-size:120px;
  display:grid;
  grid-template-columns:repeat(3,var(--cell-size));
  grid-template-rows:repeat(3,var(--cell-size));
  gap:0;
  border:2px solid var(--border);
  border-radius:14px;
  background:linear-gradient(180deg,#fff,#fbfdff);
  padding:6px;
}
.cell{position:relative;display:flex;align-items:center;justify-content:center;cursor:pointer;user-select:none;transition:all 120ms ease}
.inner{width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#fbfdff;border-left:1px solid var(--border);border-top:1px solid var(--border);font-size:48px;border-radius:8px;transition:transform 140ms ease,background 140ms ease}
.cell:nth-child(-n+3) .inner{border-top:none}
.cell:nth-child(3n+1) .inner{border-left:none}
.cell:hover .inner{background:#fffaf0;transform:translateY(-6px);box-shadow:0 8px 22px rgba(16,24,40,0.06)}
.cell.filled .inner{cursor:default;transform:none;background:#fff;box-shadow:none}
.cell.win .inner{background:var(--win);box-shadow:0 14px 36px rgba(60,180,100,0.08);transform:translateY(-6px)}
.coord{position:absolute;left:8px;top:6px;font-size:11px;color:var(--muted)}
.icon-x svg{width:54px;height:54px;display:block} .icon-o svg{width:54px;height:54px;display:block}
.icon-x svg path{stroke:var(--accent-x);stroke-width:10;stroke-linecap:round;stroke-linejoin:round;fill:none;filter:drop-shadow(0 4px 10px rgba(255,77,109,0.12))}
.icon-o svg circle{stroke:var(--accent-o);stroke-width:10;fill:none;filter:drop-shadow(0 6px 12px rgba(59,130,246,0.12))}
@media (max-width:880px){.layout{grid-template-columns:1fr;gap:12px}.board{--cell-size:28vw}.icon-x svg,.icon-o svg{width:22vw;height:22vw}}
</style>
</head>
<body>
<div class="wrap">
  <header><h1>🎯 Tic-Tac-Toe — Vs Computer (Fixed)</h1><div style="color:var(--muted)">Easy • Normal • Unbeatable</div></header>

  <div class="layout">
    <aside class="card controls">
      <div><div style="color:var(--muted);font-size:13px">Mode</div>
        <label><input type="radio" name="mode" value="two" checked> Two Players</label>
        <label><input type="radio" name="mode" value="cpu"> Vs Computer</label>
      </div>

      <label>Choose symbol
        <select id="playerSym"><option value="X">X (❌)</option><option value="O">O (⭕)</option></select>
      </label>

      <label>AI Difficulty
        <select id="aiLevel"><option>Easy</option><option selected>Normal</option><option>Unbeatable</option></select>
      </label>

      <label>Who starts?
        <select id="starter"><option>Human</option><option>Computer</option></select>
      </label>

      <div style="margin-top:12px;display:flex;gap:10px;">
        <button id="newGame" class="btn">New Game</button>
        <button id="undo" class="btn alt">Undo</button>
      </div>

      <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
        <div style="background:#f1f5f9;padding:8px 12px;border-radius:10px;font-weight:600">❌ X: <span id="scoreX">0</span></div>
        <div style="background:#f1f5f9;padding:8px 12px;border-radius:10px;font-weight:600">⭕ O: <span id="scoreO">0</span></div>
        <div style="background:#f1f5f9;padding:8px 12px;border-radius:10px;font-weight:600">🤝 Draws: <span id="scoreD">0</span></div>
      </div>

      <div style="margin-top:12px;color:var(--muted);font-size:13px">Tip: If playing vs Computer and you choose 'Computer' as starter, AI will move first.</div>
    </aside>

    <main>
      <div class="card board-wrap">
        <div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:8px;width:100%">
          <div><strong id="status">Turn: ❌ X</strong><div style="color:var(--muted);font-size:13px" id="substat">Ready</div></div>
          <div class="top-actions">
            <button id="playAgain" class="btn alt">Play Again</button>
            <button id="switchSides" class="btn alt">Switch Sides</button>
          </div>
        </div>

        <div id="board" class="board" aria-label="tic tac toe board"></div>

        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:14px;width:100%">
          <div style="flex:1"><strong>Move History</strong><div id="history" style="max-height:160px;overflow:auto;margin-top:8px;color:var(--muted)">No moves yet.</div></div>
          <div style="width:260px;padding-left:12px"><strong>Game Log</strong><div id="glog" style="margin-top:6px;color:var(--muted)">Ready.</div></div>
        </div>
      </div>
    </main>
  </div>
</div>

<script>
const EMOJI = {'X':'❌','O':'⭕','':''};
let board = Array(9).fill('');
let mode = 'two';
let playerSym = 'X';
let aiSym = 'O';
let aiLevel = 'Normal';
let starter = 'Human';
let turn = 'X';
let scores = {X:0, O:0, D:0};
let gameOver = false;
let historyArr = [];
let winningLine = [];

const boardEl = document.getElementById('board');

function svgX(){ return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M18 18 L82 82 M82 18 L18 82" stroke-linecap="round" stroke-linejoin="round"></path><style>path{stroke:var(--accent-x);stroke-width:10;}</style></svg>`; }
function svgO(){ return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="30"></circle><style>circle{stroke:var(--accent-o);stroke-width:10;fill:none;}</style></svg>`; }

function makeCell(i){
  const cell = document.createElement('div');
  cell.className = 'cell';
  cell.dataset.idx = i;
  const inner = document.createElement('div');
  inner.className = 'inner';
  const coord = document.createElement('div');
  coord.className = 'coord';
  const r = Math.floor(i/3)+1, c = (i%3)+1;
  coord.innerText = `${r},${c}`;
  inner.appendChild(coord);
  const iconWrap = document.createElement('div');
  iconWrap.className = 'icon';
  inner.appendChild(iconWrap);
  cell.appendChild(inner);

  cell.addEventListener('mouseenter', ()=>highlightRowCol(i, true));
  cell.addEventListener('mouseleave', ()=>highlightRowCol(i, false));
  return cell;
}
function highlightRowCol(idx, on){
  const row = Math.floor(idx/3), col = idx%3;
  Array.from(boardEl.children).forEach((c,i)=>{
    c.classList.remove('hover-row','hover-col');
    if(on){ if(Math.floor(i/3)===row) c.classList.add('hover-row'); if((i%3)===col) c.classList.add('hover-col'); }
  });
}

function renderBoard(){
  boardEl.innerHTML = '';
  for(let i=0;i<9;i++){
    const cell = makeCell(i);
    const inner = cell.querySelector('.inner');
    if(board[i]){
      cell.classList.add('filled');
      cell.querySelector('.icon').innerHTML = board[i]==='X' ? `<span class="icon-x">${svgX()}</span>` : `<span class="icon-o">${svgO()}</span>`;
    } else {
      cell.addEventListener('click', ()=>onCellClick(i), {passive:true});
    }
    if(winningLine.includes(i)) cell.classList.add('win');
    boardEl.appendChild(cell);
  }
  document.getElementById('status').innerText = gameOver ? (winningLine.length ? `${EMOJI[turn==='X' ? 'X':'O']} ${turn} wins!` : 'Draw') : `Turn: ${EMOJI[turn]} ${turn}`;
  document.getElementById('glog').innerText = gameOver ? (winningLine.length ? `${EMOJI[turn]} ${turn} wins!` : 'Game ended in a draw') : 'Game in progress...';
  renderHistory();
}
function renderHistory(){
  const h = document.getElementById('history');
  if(historyArr.length===0) h.innerHTML = '<div style="color:var(--muted)">No moves yet.</div>';
  else h.innerHTML = historyArr.map((it,i)=>`<div>${i+1}. ${EMOJI[it.sym]} ${it.sym} → row ${Math.floor(it.idx/3)+1}, col ${(it.idx%3)+1}</div>`).join('');
  document.getElementById('scoreX').innerText = scores.X;
  document.getElementById('scoreO').innerText = scores.O;
  document.getElementById('scoreD').innerText = scores.D;
}

function checkWinnerLocal(){
  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for(const [a,b,c] of lines) if(board[a] && board[a]===board[b] && board[b]===board[c]) return {winner:board[a], line:[a,b,c]};
  if(board.every(x=>x)) return {winner:'Draw', line:[]};
  return {winner:null, line:[]};
}

// Player click handler
async function onCellClick(i){
  if(gameOver || board[i]) return;
  // Only allow player to click on their turn
  if(mode === 'cpu' && turn !== playerSym) return;
  // Two players: allow any turn
  board[i] = turn;
  historyArr.push({sym: turn, idx: i});
  const res = checkWinnerLocal();
  if(res.winner){
    gameOver = true; winningLine = res.line;
    if(res.winner === 'Draw') scores.D++; else scores[res.winner]++;
    renderBoard();
    return;
  } else {
    // swap turn
    turn = (turn === 'X') ? 'O' : 'X';
    renderBoard();
  }

  // If vs CPU and it's AI's turn, ask server
  if(mode === 'cpu' && turn === aiSym && !gameOver){
    await aiMove();
  }
}

// Ask server for AI move
async function aiMove(){
  document.getElementById('glog').innerText = 'AI thinking...';
  try {
    const resp = await fetch('/ai_move', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ board: board, ai_sym: aiSym, level: aiLevel })
    });
    const data = await resp.json();
    const idx = data.move;
    await new Promise(r => setTimeout(r, 180 + Math.random()*160)); // small UX delay
    if(idx != null && !board[idx]){
      board[idx] = aiSym;
      historyArr.push({sym: aiSym, idx});
      const res = checkWinnerLocal();
      if(res.winner){
        gameOver = true; winningLine = res.line;
        if(res.winner === 'Draw') scores.D++; else scores[res.winner]++;
      } else {
        turn = (turn === 'X') ? 'O' : 'X';
      }
      renderBoard();
    } else {
      document.getElementById('glog').innerText = 'AI returned invalid move.';
    }
  } catch(err){
    document.getElementById('glog').innerText = 'AI request failed.';
    console.error(err);
  }
}

function newGame(keepScores=false){
  board = Array(9).fill('');
  historyArr = [];
  winningLine = [];
  gameOver = false;
  mode = document.querySelector('input[name=mode]:checked').value;
  playerSym = document.getElementById('playerSym').value;
  aiSym = (playerSym === 'X') ? 'O' : 'X';
  aiLevel = document.getElementById('aiLevel').value;
  starter = document.getElementById('starter').value;
  // if two players — first player is X by convention unless player chose otherwise:
  if(mode === 'two'){
    // decide starting symbol: make X start always for two players
    turn = 'X';
  } else {
    // vs CPU: starter selection matters
    turn = (starter === 'Computer') ? aiSym : playerSym;
  }
  if(!keepScores) { /* keep scores by default; use separate Reset if needed */ }
  renderBoard();
  // If AI starts, perform AI move
  if(mode === 'cpu' && turn === aiSym){
    aiMove();
  }
}

// Undo: if vs CPU, undo last 2 moves (player+AI) to return to player's turn; otherwise undo last move
function undo(){
  if(historyArr.length === 0 || gameOver) return;
  if(mode === 'cpu'){
    // remove AI move if present
    // undo up to 2 moves
    const popCount = Math.min(2, historyArr.length);
    for(let i=0;i<popCount;i++){
      const last = historyArr.pop();
      board[last.idx] = '';
    }
    // set turn to player
    turn = playerSym;
    winningLine = [];
    gameOver = false;
    renderBoard();
  } else {
    const last = historyArr.pop();
    board[last.idx] = '';
    turn = last.sym;
    winningLine = [];
    gameOver = false;
    renderBoard();
  }
}

document.addEventListener('DOMContentLoaded', ()=>{
  // Attach controls
  document.getElementById('newGame').addEventListener('click', ()=>newGame(true));
  document.getElementById('undo').addEventListener('click', undo);
  document.getElementById('playAgain').addEventListener('click', ()=>newGame(true));
  document.getElementById('switchSides').addEventListener('click', ()=>{
    const cur = document.getElementById('playerSym').value;
    document.getElementById('playerSym').value = cur === 'X' ? 'O' : 'X';
    newGame(true);
  });
  document.querySelectorAll('input[name=mode]').forEach(r=>r.addEventListener('change', ()=>{
    if(document.querySelector('input[name=mode]:checked').value === 'two'){
      document.getElementById('aiLevel').disabled = true;
      document.getElementById('starter').disabled = true;
    } else {
      document.getElementById('aiLevel').disabled = false;
      document.getElementById('starter').disabled = false;
    }
    newGame(true);
  }));
  // initialize controls defaults
  if(document.querySelector('input[name=mode]:checked').value === 'two'){
    document.getElementById('aiLevel').disabled = true;
    document.getElementById('starter').disabled = true;
  }
  newGame(true);
});
</script>
</body>
</html>
    """)

@app.route('/ai_move', methods=['POST'])
def ai_move():
    data = request.get_json(force=True)
    board = data.get('board', [])
    ai_sym = data.get('ai_sym', 'O')
    level = data.get('level', 'Normal')
    # Validate
    if not isinstance(board, list) or len(board) != 9:
        return jsonify({'error': 'bad board'}), 400
    board = [cell if cell in ('X', 'O') else '' for cell in board]

    empty = [i for i, v in enumerate(board) if not v]
    if not empty:
        return jsonify({'move': None})

    # Easy: random
    if level == 'Easy':
        return jsonify({'move': random.choice(empty)})

    # Determine human symbol
    human_sym = 'O' if ai_sym == 'X' else 'X'

    # Quick tactical checks before Minimax for speed/readability:
    # 1) Win if possible
    for i in empty:
        board[i] = ai_sym
        winner, _ = check_winner(board)
        board[i] = ''
        if winner == ai_sym:
            return jsonify({'move': i})
    # 2) Block opponent immediate win
    for i in empty:
        board[i] = human_sym
        winner, _ = check_winner(board)
        board[i] = ''
        if winner == human_sym:
            return jsonify({'move': i})

    # Normal: sometimes random to be beatable
    if level == 'Normal' and random.random() < 0.22:
        return jsonify({'move': random.choice(empty)})

    # Unbeatable/normal: minimax with alpha-beta
    _, move = minimax(board, 0, True, ai_sym, human_sym)
    if move is None:
        move = random.choice(empty)
    return jsonify({'move': move})

if __name__ == '__main__':
    app.run(debug=True)
