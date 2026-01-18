	const { createApp } = Vue;
	createApp({
	    data() {
	        return {
	            apiBase: 'http://127.0.0.1:8000', // 后端地址
	            isDragOver: false,
	            loading: false,
	            uploadedFile: null, // { filename, original_filename, rows, columns }
	            // 当前选中的列
	            selectedCol: {
	                stats: '',
	                sort: '',
	                group: '',
	                agg: ''
	            },
	            // 图表配置
	            chartConfig: {
	                type: 'bar',
	                label: '',
	                value: ''
	            },
	            // 结果展示
	            cleanResult: null,
	            statsResult: null,
	            tableData: [], // 用于排序、分组聚合结果
	            chartInstance: null,
	            // 壁纸设置
	            isDefaultBg: true,
	            currentWallpaper: ''
	        }
	    },
	    methods: {
	        // 壁纸切换逻辑
	        toggleWallpaper() {
	            this.isDefaultBg = !this.isDefaultBg;
	            if (!this.isDefaultBg) {
	                // 使用随机种子图
	                const seed = Math.random().toString(36).substring(7);
	                this.currentWallpaper = `https://picsum.photos/seed/${seed}/1920/1080`;
	            }
	        },
	        // 文件处理
	        handleDrop(e) {
	            this.isDragOver = false;
	            const files = e.dataTransfer.files;
	            if (files.length) this.uploadFile(files[0]);
	        },
	        handleFileSelect(e) {
	            const files = e.target.files;
	            if (files.length) this.uploadFile(files[0]);
	        },
	        async uploadFile(file) {
	            this.loading = true;
	            const formData = new FormData();
	            formData.append('file', file);
	            try {
	                const res = await axios.post(`${this.apiBase}/upload`, formData, {
	                    headers: { 'Content-Type': 'multipart/form-data' }
	                });
	                this.uploadedFile = res.data;
	                // 默认选中第一列和第二列作为初始选择
	                if (this.uploadedFile.columns.length > 0) {
	                    this.selectedCol.stats = this.uploadedFile.columns[0];
	                    this.selectedCol.sort = this.uploadedFile.columns[0];
	                    this.chartConfig.label = this.uploadedFile.columns[0];
	                    if (this.uploadedFile.columns.length > 1) {
	                        this.selectedCol.agg = this.uploadedFile.columns[1];
	                        this.chartConfig.value = this.uploadedFile.columns[1];
	                    } else {
	                        this.selectedCol.agg = this.uploadedFile.columns[0];
	                        this.chartConfig.value = this.uploadedFile.columns[0];
	                    }
	                }
	            } catch (err) {
	                alert('上传失败: ' + (err.response?.data?.detail || err.message));
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 数据清洗
	        async cleanData() {
	            this.loading = true;
	            try {
	                const res = await axios.post(`${this.apiBase}/analyze/clean`, {
	                    filename: this.uploadedFile.filename
	                });
	                this.cleanResult = res.data;
	                alert('清洗完成');
	            } catch (err) {
	                alert('清洗失败');
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 统计分析
	        async getStats() {
	            this.loading = true;
	            try {
	                const res = await axios.post(`${this.apiBase}/analyze/stats`, {
	                    filename: this.uploadedFile.filename,
	                    column: this.selectedCol.stats
	                });
	                this.statsResult = res.data.stats;
	            } catch (err) {
	                console.error(err);
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 排序
	        async sortData() {
	            this.loading = true;
	            try {
	                const res = await axios.post(`${this.apiBase}/analyze/sort`, {
	                    filename: this.uploadedFile.filename,
	                    column: this.selectedCol.sort,
	                    order: 'desc' // 默认降序
	                });
	                this.tableData = res.data.data;
	            } catch (err) {
	                console.error(err);
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 分组聚合
	        async groupData() {
	            this.loading = true;
	            try {
	                const res = await axios.post(`${this.apiBase}/analyze/group`, {
	                    filename: this.uploadedFile.filename,
	                    group_col: this.selectedCol.group,
	                    agg_col: this.selectedCol.agg,
	                    method: 'sum'
	                });
	                this.tableData = res.data.data;
	            } catch (err) {
	                alert('分组失败，请检查列类型');
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 生成图表 (包括热力图)
	        async generateChart(isHeatmap = false) {
	            this.loading = true;
	            this.tableData = []; // 隐藏表格
	            this.statsResult = null; // 隐藏统计
	            try {
	                let payload = {
	                    filename: this.uploadedFile.filename,
	                    type: isHeatmap ? 'heatmap' : this.chartConfig.type
	                };
	                if (!isHeatmap) {
	                    payload.label_col = this.chartConfig.label;
	                    payload.value_col = this.chartConfig.value;
	                } else {
	                    // 热力图不需要指定具体列，或者可以传空
	                    payload.label_col = "";
	                    payload.value_col = "";
	                }
	                const res = await axios.post(`${this.apiBase}/analyze/chart`, payload);
	                this.renderChart(res.data.chart_config);
	            } catch (err) {
	                console.error(err);
	            } finally {
	                this.loading = false;
	            }
	        },
	        // 相关性分析 (生成热力图)
	        getCorrelation() {
	            this.generateChart(true);
	        },
	        // 渲染 ECharts
	        renderChart(config) {
	            const chartDom = document.getElementById('chart-container');
	            if (!chartDom) return;
	            // 销毁旧实例
	            if (this.chartInstance) {
	                this.chartInstance.dispose();
	            }
	            this.chartInstance = echarts.init(chartDom);
	            let option = {};
	            if (config.type === 'heatmap') {
	                option = {
	                    tooltip: { position: 'top' },
	                    grid: { height: '70%', top: '10%' },
	                    xAxis: { type: 'category', data: config.x_axis, splitArea: { show: true } },
	                    yAxis: { type: 'category', data: config.y_axis, splitArea: { show: true } },
	                    visualMap: { min: -1, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%' },
	                    series: [{
	                        name: 'Correlation',
	                        type: 'heatmap',
	                        data: config.data,
	                        label: { show: true },
	                        emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
	                    }]
	                };
	            } else if (config.type === 'pie') {
	                option = {
	                    tooltip: { trigger: 'item' },
	                    legend: { top: '5%', left: 'center' },
	                    series: [{
	                        name: 'Data',
	                        type: 'pie',
	                        radius: ['40%', '70%'],
	                        avoidLabelOverlap: false,
	                        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
	                        label: { show: false, position: 'center' },
	                        emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
	                        data: config.data
	                    }]
	                };
	            } else if (config.type === 'line' || config.type === 'bar') {
	                option = {
	                    tooltip: { trigger: 'axis' },
	                    xAxis: { type: 'category', data: config.data.map(item => item.name || item[0]) },
	                    yAxis: { type: 'value' },
	                    series: [{
	                        data: config.data.map(item => item.value || item[1]),
	                        type: config.type,
	                        smooth: true,
	                        itemStyle: { color: '#00d2ff' }
	                    }]
	                };
	            }
	            this.chartInstance.setOption(option);
	        }
	    },
	    mounted() {
	        // 初始化窗口大小改变监听，重绘图表
	        window.addEventListener('resize', () => {
	            if (this.chartInstance) this.chartInstance.resize();
	        });
	    }
	}).mount('#app');