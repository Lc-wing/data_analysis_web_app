	// 背景动画逻辑：卫星光标旋转
	document.addEventListener('DOMContentLoaded', () => {
	    const canvas = document.getElementById('bg-canvas');
	    const ctx = canvas.getContext('2d');
	    let width, height;
	    let mouseX = -1000, mouseY = -1000; // 初始在屏幕外
	    // 卫星配置
	    const satellites = [
	        { color: '#00d2ff', radius: 40, speed: 0.02, size: 4, angle: 0 },
	        { color: '#ff007f', radius: 70, speed: -0.03, size: 6, angle: 2 },
	        { color: '#ffe600', radius: 100, speed: 0.015, size: 3, angle: 4 }
	    ];
	    function resize() {
	        width = window.innerWidth;
	        height = window.innerHeight;
	        canvas.width = width;
	        canvas.height = height;
	    }
	    window.addEventListener('resize', resize);
	    window.addEventListener('mousemove', (e) => {
	        mouseX = e.clientX;
	        mouseY = e.clientY;
	    });
	    resize();
	    function animate() {
	        // 清空画布，保留微弱拖尾效果
	        ctx.fillStyle = 'rgba(15, 32, 39, 0.2)'; // 对应CSS的冷色基调
	        ctx.fillRect(0, 0, width, height);
	        // 绘制冷色渐变背景叠加
	        const gradient = ctx.createLinearGradient(0, 0, width, height);
	        gradient.addColorStop(0, '#0f2027');
	        gradient.addColorStop(0.5, '#203a43');
	        gradient.addColorStop(1, '#2c5364');
	        ctx.fillStyle = gradient;
	        ctx.fillRect(0, 0, width, height);
	        // 如果鼠标在屏幕内，绘制卫星
	        if (mouseX > 0) {
	            satellites.forEach(sat => {
	                // 更新角度
	                sat.angle += sat.speed;
	                // 计算位置
	                const x = mouseX + Math.cos(sat.angle) * sat.radius;
	                const y = mouseY + Math.sin(sat.angle) * sat.radius;
	                // 绘制光晕
	                const glow = ctx.createRadialGradient(x, y, 0, x, y, sat.size * 3);
	                glow.addColorStop(0, sat.color);
	                glow.addColorStop(1, 'rgba(0,0,0,0)');
	                ctx.fillStyle = glow;
	                ctx.beginPath();
	                ctx.arc(x, y, sat.size * 3, 0, Math.PI * 2);
	                ctx.fill();
	                // 绘制核心
	                ctx.fillStyle = '#fff';
	                ctx.beginPath();
	                ctx.arc(x, y, sat.size, 0, Math.PI * 2);
	                ctx.fill();
	                // 绘制轨道线 (可选，增加科技感)
	                ctx.strokeStyle = `rgba(255, 255, 255, 0.05)`;
	                ctx.beginPath();
	                ctx.arc(mouseX, mouseY, sat.radius, 0, Math.PI * 2);
	                ctx.stroke();
	            });
	        }
	        requestAnimationFrame(animate);
	    }
	    animate();
	});