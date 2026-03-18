// 新闻筛选功能
document.addEventListener('DOMContentLoaded', function() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const newsCards = document.querySelectorAll('.news-card');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // 更新按钮状态
            navBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 筛选新闻
            const filter = this.dataset.filter;
            
            newsCards.forEach(card => {
                if (filter === 'all' || card.dataset.lang === filter) {
                    card.classList.remove('hidden');
                    card.style.animation = 'fadeIn 0.5s';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
});

// 添加淡入动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .news-card {
        animation: fadeIn 0.5s ease-out;
    }
`;
document.head.appendChild(style);
