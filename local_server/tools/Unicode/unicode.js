/* ============================================================
   Minecraft Unicode 字符表 · 页面交互
   复制能力完全复用 copy_text.js（read_text / clipboard.copy），
   这里只重做「交互与反馈」：
     · 点按任意字符 → 直接复制
     · 鼠标悬停 / 键盘方向键 → 预览该格编码
     · 轻提示（toast）替代原来「清空输入框 3 秒」的提示方式
     · 批量框实时预览与格式校验
   ============================================================ */

(function () {
    'use strict';

    var RE_ONE = /^\\u[a-fA-F0-9]{4}$/;
    var RE_RANGE = /^\\u[a-fA-F0-9]{4}~\\u[a-fA-F0-9]{4}$/;
    var GRID = 16;                       // 每张字符图是 16 × 16 格
    var INVISIBLE = [
        [0x00, 0x1F], [0x7F, 0xA0], [0xAD, 0xAD], [0x200B, 0x200F],
        [0x202A, 0x202E], [0x2060, 0x2064], [0xFEFF, 0xFEFF]
    ];

    function $(id) {
        return document.getElementById(id);
    }

    function hex4(n) {
        return ('000' + n.toString(16).toUpperCase()).slice(-4);
    }

    function isInvisible(code) {
        for (var i = 0; i < INVISIBLE.length; i++) {
            if (code >= INVISIBLE[i][0] && code <= INVISIBLE[i][1]) return true;
        }
        return false;
    }

    /* ---------- 解析：与 copy_text.js 的 read_text 完全同一套规则 ---------- */
    function parseLines(text) {
        var lines = text.split('\n');
        var chars = [];
        var bad = [];
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (RE_ONE.test(line)) {
                chars.push(String.fromCharCode(parseInt(line.slice(2), 16)));
            } else if (RE_RANGE.test(line)) {
                var start = parseInt(line.split('~')[0].slice(2), 16);
                var end = parseInt(line.split('~')[1].slice(2), 16);
                for (var c = start; c <= end; c++) chars.push(String.fromCharCode(c));
            } else {
                bad.push(i + 1);
            }
        }
        return { chars: chars, bad: bad, lines: lines.length };
    }

    /* ---------- 轻提示 ---------- */
    var toastEl = null;
    var toastTimer = 0;

    function toast(opts) {
        if (!toastEl) {
            toastEl = document.createElement('div');
            toastEl.setAttribute('role', 'status');
            toastEl.setAttribute('aria-live', 'polite');
            document.body.appendChild(toastEl);
        }
        toastEl.className = 'toast' + (opts.error ? ' err' : '');
        while (toastEl.firstChild) toastEl.removeChild(toastEl.firstChild);

        if (typeof opts.glyph === 'string') {
            var glyph = document.createElement('span');
            glyph.className = 'toast-glyph';
            glyph.textContent = opts.glyph;
            toastEl.appendChild(glyph);
        }

        var body = document.createElement('div');
        var title = document.createElement('div');
        title.className = 'toast-title';
        title.textContent = opts.title;
        body.appendChild(title);

        if (opts.sub) {
            var sub = document.createElement('div');
            sub.className = 'toast-sub';
            sub.textContent = opts.sub;
            body.appendChild(sub);
        }
        toastEl.appendChild(body);

        void toastEl.offsetWidth;                 // 重排一次，让动画能重放
        toastEl.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () {
            toastEl.classList.remove('show');
        }, opts.error ? 3600 : 2400);
    }

    /* ---------- 单个字符复制 ---------- */
    function copyCell(tile, row, col) {
        var code = parseInt(tile.getAttribute('data-base'), 10) + row * GRID + col;
        var ch = String.fromCharCode(code);

        if (!window.clipboard || typeof window.clipboard.copy !== 'function') {
            toast({ error: true, title: '复制组件未加载', sub: '请检查 copy_text.js 是否可访问' });
            return;
        }

        window.clipboard.copy(ch);               // 复用原有复制实现
        flash(tile, row, col);

        var note = 'U+' + hex4(code);
        if (isInvisible(code)) {
            note += code === 0x20 ? ' · 空格' : ' · 不可见字符';
        }
        toast({ glyph: ch, title: '已复制', sub: note });
    }

    function flash(tile, row, col) {
        var mark = document.createElement('span');
        mark.className = 'mark';
        mark.setAttribute('aria-hidden', 'true');
        mark.style.left = (col * 100 / GRID) + '%';
        mark.style.top = (row * 100 / GRID) + '%';
        tile.appendChild(mark);
        mark.addEventListener('animationend', function () {
            if (mark.parentNode) mark.parentNode.removeChild(mark);
        });
    }

    /* ---------- 悬停 / 聚焦时的高亮格与编码提示 ---------- */
    function overlayFor(tile) {
        if (tile.__ov) return tile.__ov;
        var cell = document.createElement('span');
        cell.className = 'cell';
        cell.setAttribute('aria-hidden', 'true');
        var tip = document.createElement('span');
        tip.className = 'tip';
        tip.setAttribute('aria-hidden', 'true');
        tile.appendChild(cell);
        tile.appendChild(tip);
        tile.__ov = { cell: cell, tip: tip };
        return tile.__ov;
    }

    function showCell(tile, row, col) {
        var ov = overlayFor(tile);
        var code = parseInt(tile.getAttribute('data-base'), 10) + row * GRID + col;

        ov.cell.style.left = (col * 100 / GRID) + '%';
        ov.cell.style.top = (row * 100 / GRID) + '%';
        ov.cell.classList.add('on');

        ov.tip.textContent = '\\u' + hex4(code);
        ov.tip.classList.add('on');

        var w = tile.clientWidth;
        var h = tile.clientHeight;
        var tw = ov.tip.offsetWidth;
        var th = ov.tip.offsetHeight;
        var cx = (col + .5) * w / GRID;
        var cy = (row + .5) * h / GRID;
        var left = Math.min(Math.max(cx - tw / 2, 3), Math.max(3, w - tw - 3));
        var top = cy - th - 4;
        if (top < 2) top = cy + 4;
        ov.tip.style.left = left + 'px';
        ov.tip.style.top = top + 'px';
    }

    function hideCell(tile) {
        if (!tile.__ov) return;
        tile.__ov.cell.classList.remove('on');
        tile.__ov.tip.classList.remove('on');
    }

    function cellFrom(tile, clientX, clientY) {
        var rect = tile.getBoundingClientRect();
        if (!rect.width || !rect.height) return null;
        var x = (clientX - rect.left) / rect.width;
        var y = (clientY - rect.top) / rect.height;
        if (x < 0 || x >= 1 || y < 0 || y >= 1) return null;
        return {
            col: Math.min(GRID - 1, Math.floor(x * GRID)),
            row: Math.min(GRID - 1, Math.floor(y * GRID))
        };
    }

    function setupAtlas(tile) {
        tile.addEventListener('click', function (e) {
            var pos = cellFrom(tile, e.clientX, e.clientY);
            if (!pos) return;
            tile.__row = pos.row;
            tile.__col = pos.col;
            copyCell(tile, pos.row, pos.col);
        });

        tile.addEventListener('pointermove', function (e) {
            if (e.pointerType !== 'mouse') return;
            var pos = cellFrom(tile, e.clientX, e.clientY);
            if (!pos) {
                hideCell(tile);
                return;
            }
            tile.__row = pos.row;
            tile.__col = pos.col;
            showCell(tile, pos.row, pos.col);
        });

        tile.addEventListener('pointerleave', function () {
            if (document.activeElement !== tile) hideCell(tile);
        });

        tile.addEventListener('focus', function () {
            showCell(tile, tile.__row || 0, tile.__col || 0);
        });

        tile.addEventListener('blur', function () {
            hideCell(tile);
        });

        tile.addEventListener('keydown', function (e) {
            var row = tile.__row || 0;
            var col = tile.__col || 0;
            var moved = true;

            switch (e.key) {
                case 'ArrowLeft': col = Math.max(0, col - 1); break;
                case 'ArrowRight': col = Math.min(GRID - 1, col + 1); break;
                case 'ArrowUp': row = Math.max(0, row - 1); break;
                case 'ArrowDown': row = Math.min(GRID - 1, row + 1); break;
                case 'Home': row = 0; col = 0; break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    copyCell(tile, row, col);
                    return;
                default:
                    moved = false;
            }
            if (!moved) return;

            e.preventDefault();
            tile.__row = row;
            tile.__col = col;
            showCell(tile, row, col);
        });
    }

    /* ---------- 批量框预览 ---------- */
    function renderPreview() {
        var input = $('input_box_1');
        var out = $('outside_clip_board');
        var stat = $('batch_stat');
        if (!input || !out) return;

        var text = input.value;
        var res = parseLines(text);
        while (out.firstChild) out.removeChild(out.firstChild);

        if (!text) {
            out.textContent = '等待输入 · 每行一条编码';
            if (stat) stat.textContent = '0 行';
            return;
        }
        if (stat) stat.textContent = res.lines + ' 行';

        if (res.bad.length) {
            var bad = document.createElement('span');
            bad.className = 'bad';
            bad.textContent = '第 ' + res.bad.slice(0, 6).join('、') + ' 行格式有误';
            out.appendChild(bad);
            if (res.bad.length > 6) {
                var rest = document.createElement('span');
                rest.className = 'bad';
                rest.textContent = ' 等 ' + res.bad.length + ' 行';
                out.appendChild(rest);
            }
            return;
        }

        var head = document.createElement('span');
        head.appendChild(document.createTextNode('将复制 '));
        var count = document.createElement('b');
        count.textContent = String(res.chars.length);
        head.appendChild(count);
        head.appendChild(document.createTextNode(' 个字符'));
        out.appendChild(head);

        var all = res.chars.join('');
        var box = document.createElement('div');
        box.className = 'preview';
        box.textContent = all ? (all.length > 72 ? all.slice(0, 72) + '…' : all) : '（无输出）';
        out.appendChild(box);
    }

    /* 页面里 oninput="displayResult(...)" 调用的就是它 */
    window.displayResult = function () {
        renderPreview();
    };

    window.clear_batch = function () {
        var input = $('input_box_1');
        if (!input) return;
        input.value = '';
        renderPreview();
        input.focus();
    };

    /* copy_text.js 的 read_text() 通过 set_timer() 反馈结果；
       原实现会清空输入框 3 秒，这里改为轻提示，输入内容保持不变。 */
    window.set_timer = function (text1) {
        var msg = String(text1 == null ? '' : text1).replace(/\s*3秒后自动返回[\s\S]*$/, '').trim();
        if (/出错/.test(msg)) {
            toast({
                error: true,
                title: msg,
                sub: '格式：\\uXXXX 或 \\uXXXX~\\uXXXX（每行一条）'
            });
            return;
        }
        var input = $('input_box_1');
        var total = input ? parseLines(input.value).chars.length : 0;
        toast({ title: total ? '已复制 ' + total + ' 个字符' : '已复制到剪贴板' });
    };

    /* ---------- 翻页 ---------- */
    var pageNo = parseInt(document.body.getAttribute('data-page'), 10) || 1;
    var pageTotal = parseInt(document.body.getAttribute('data-total'), 10) || 3;

    function wirePager() {
        var btns = document.querySelectorAll('[data-nav]');
        for (var i = 0; i < btns.length; i++) {
            var target = pageNo + parseInt(btns[i].getAttribute('data-nav'), 10);
            var ok = target >= 1 && target <= pageTotal;
            btns[i].disabled = !ok;
            if (!ok) btns[i].setAttribute('aria-disabled', 'true');
        }
    }

    document.addEventListener('keydown', function (e) {
        if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey) return;
        var t = e.target;
        if (t && (t.tagName === 'TEXTAREA' || t.tagName === 'INPUT' || t.isContentEditable)) return;
        if (typeof window.change_page !== 'function') return;
        if (e.key === 'ArrowLeft') window.change_page(-1);
        else if (e.key === 'ArrowRight') window.change_page(1);
    });

    /* ---------- 启动 ---------- */
    function init() {
        var tiles = document.querySelectorAll('.atlas');
        for (var i = 0; i < tiles.length; i++) setupAtlas(tiles[i]);
        wirePager();
        renderPreview();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
