// clipboard_paste.js - MiniMax H3 Clipboard Image Paste Handler & Toast System

(function() {
    // 1. Inject CSS for hover indicator, success pulse, floating button and toast notifications
    const style = document.createElement('style');
    style.textContent = `
        .clipboard-image-target {
            position: relative !important;
            transition: all 0.25s ease-in-out !important;
        }
        .clipboard-target-hover {
            outline: 2px dashed #a855f7 !important;
            outline-offset: 3px !important;
            box-shadow: 0 0 16px rgba(168, 85, 247, 0.45) !important;
        }
        .clipboard-target-success {
            outline: 2px solid #22c55e !important;
            outline-offset: 3px !important;
            box-shadow: 0 0 24px rgba(34, 197, 94, 0.6) !important;
            animation: clipPulse 1.2s ease-out !important;
        }
        @keyframes clipPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.012); }
            100% { transform: scale(1); }
        }
        #clipboard-toast-container {
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }
        .clipboard-toast {
            background: rgba(18, 18, 30, 0.95);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(168, 85, 247, 0.5);
            border-left: 4px solid #a855f7;
            border-radius: 8px;
            color: #f8fafc;
            padding: 12px 18px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 0 15px rgba(168, 85, 247, 0.2);
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: auto;
            max-width: 440px;
        }
        .clipboard-toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        .clipboard-toast-icon {
            font-size: 18px;
            flex-shrink: 0;
        }
        .clipboard-toast-body {
            flex-grow: 1;
            line-height: 1.4;
        }
    `;
    document.head.appendChild(style);

    // 2. Toast Notification Function
    function showToast(message, type = 'info') {
        let container = document.getElementById('clipboard-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'clipboard-toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = 'clipboard-toast';
        const icon = type === 'success' ? '✅' : type === 'warn' ? '⚠️' : '📋';
        if (type === 'success') {
            toast.style.borderLeftColor = '#22c55e';
        } else if (type === 'warn') {
            toast.style.borderLeftColor = '#eab308';
        }
        toast.innerHTML = `<span class="clipboard-toast-icon">${icon}</span><span class="clipboard-toast-body">${message}</span>`;
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 3200);
    }

    // 3. Hover Tracking
    let activeHoveredTarget = null;
    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('.clipboard-image-target');
        if (target) {
            if (activeHoveredTarget && activeHoveredTarget !== target) {
                activeHoveredTarget.classList.remove('clipboard-target-hover');
            }
            activeHoveredTarget = target;
            target.classList.add('clipboard-target-hover');
        }
    });

    document.addEventListener('mouseout', (e) => {
        const target = e.target.closest('.clipboard-image-target');
        if (target && target === activeHoveredTarget) {
            const rel = e.relatedTarget;
            if (!rel || !target.contains(rel)) {
                target.classList.remove('clipboard-target-hover');
                activeHoveredTarget = null;
            }
        }
    });

    // 4. Find Best Target in Active Tab
    function getBestTarget() {
        if (activeHoveredTarget && document.body.contains(activeHoveredTarget)) {
            return activeHoveredTarget;
        }

        // Find active tabpanel
        const panels = Array.from(document.querySelectorAll('[role="tabpanel"], .tabitem'));
        const activePanel = panels.find(p => {
            const style = window.getComputedStyle(p);
            return style.display !== 'none' && style.visibility !== 'hidden';
        });

        if (!activePanel) return null;

        const targets = Array.from(activePanel.querySelectorAll('.clipboard-image-target'));
        if (targets.length === 0) {
            // Fallback: look for any block containing an image file input
            const fileInputs = Array.from(activePanel.querySelectorAll('input[type="file"]')).filter(inp => 
                !inp.accept || inp.accept.includes('image') || inp.accept === '*'
            );
            if (fileInputs.length > 0) {
                return fileInputs[0].closest('.block') || fileInputs[0].parentElement;
            }
            return null;
        }

        if (targets.length === 1) {
            return targets[0];
        }

        // Multiple targets in the active tab (e.g. 首尾幀 or 修圖)
        // Check if first target already has an image
        const first = targets[0];
        const second = targets[1];
        const firstHasImage = first.querySelector('img') || first.querySelector('.preview') || first.querySelector('[data-testid="clear-button"]') || first.querySelector('button[aria-label="Clear"]');
        if (firstHasImage && second) {
            return second;
        }
        return first;
    }

    // 5. Inject File into Target Container
    function injectImageFile(file, targetContainer) {
        if (!targetContainer) {
            showToast('未找到可貼上的圖片欄位，請切換至有圖片上傳的分頁', 'warn');
            return false;
        }

        // Find file input inside container
        let input = targetContainer.querySelector('input[type="file"]');
        if (!input) {
            // Check if there is an input nearby in the block
            input = targetContainer.closest('.block')?.querySelector('input[type="file"]');
        }

        if (!input) {
            showToast('找不到圖片上傳控制項', 'warn');
            return false;
        }

        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new Event('input', { bubbles: true }));

        // Visual flash feedback
        targetContainer.classList.add('clipboard-target-success');
        setTimeout(() => {
            targetContainer.classList.remove('clipboard-target-success');
        }, 1200);

        // Get readable label
        let label = targetContainer.querySelector('label, .label-wrap, [data-testid="block-label"], .block-label')?.innerText?.trim() || '圖片欄位';
        label = label.replace(/[\n\r]+/g, ' ').slice(0, 30);
        showToast(`已成功從剪貼簿貼上圖片：${file.name} 至【${label}】！`, 'success');
        return true;
    }

    // 6. Global Paste Event Listener
    window.addEventListener('paste', (e) => {
        const items = (e.clipboardData || e.originalEvent?.clipboardData)?.items;
        if (!items || items.length === 0) return;

        let imageItem = null;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type && items[i].type.indexOf('image') !== -1) {
                imageItem = items[i];
                break;
            }
        }

        // If no image in clipboard, allow default paste (text)
        if (!imageItem) return;

        // Prevent default browser paste when pasting an image
        e.preventDefault();
        e.stopPropagation();

        const blob = imageItem.getAsFile();
        if (!blob) return;

        const now = new Date();
        const pad = (n) => String(n).padStart(2, '0');
        const ts = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
        const ext = blob.type === 'image/jpeg' ? '.jpg' : blob.type === 'image/webp' ? '.webp' : '.png';
        const file = new File([blob], `clipboard_${ts}${ext}`, { type: blob.type });

        const target = getBestTarget();
        injectImageFile(file, target);
    }, true);
})();
