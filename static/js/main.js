// 颜色配置
const colorScale = ['#2c0772', '#3d208e', '#8D7DFF', '#CDCCFF', '#C7FFFB', '#ff2c6d', '#564b43', '#161d33'];

// 初始化所有图表
function initCharts() {
    updateBarChart();
    updatePieChart();
    updateMixChart();
    updateHeatmap();
    updateArticleList();
}


async function updateBarChart() {
    try {
        const response = await axios.get('/api/quarter');
        const resData = response.data;

        // 检查后端响应是否正确
        if (resData.code !== 200 || !resData.data) {
            console.error('后端返回错误或无有效数据');
            return;
        }

        // console.log(resData.data); // 调试输出

        // 提取后端返回的数据
        const chartData = resData.data;

        // 提取维度和源数据，转换为 ECharts 支持的格式
        const dimensions = [...Object.keys(chartData[0]).filter(key => key !== 'category')];
        const source = chartData.map(item => ({
            product: item.category, // 柱状图 X 轴对应的分类名称
            ...item // 动态展开年份或季度的键值对
        }));

        // console.log('Dimensions:', dimensions); // 调试输出
        // console.log('Source:', source); // 调试输出

        // 配置 ECharts 图表选项
        const option = {
            legend: {}, // 自动生成图例
            tooltip: {},
            dataset: {
                dimensions: dimensions, // 动态生成维度
                source: source // 数据源
            },
            xAxis: {type: 'category'}, // X 轴为分类轴
            yAxis: {}, // Y 轴默认配置
            series: dimensions.slice(1).map(dim => ({type: 'bar', name: dim})) // 动态生成多个柱状图系列
        };

        // 渲染 ECharts 图表
        const chart = echarts.init(document.getElementById('bar'));
        chart.setOption(option);

        // 绑定点击事件
        chart.on('click', function (params) {
            if (params && params.name && params.seriesName) {
                const clickedCategory = params.name; // 获取点击的分类名称（X轴的值）
                const clickedSeries = params.seriesName; // 获取点击的系列名称（对应维度的值）
                console.log(`点击了分类: ${clickedCategory}, 系列: ${clickedSeries}`);
                // 调用更新函数，并传递详细信息
                updateArticleList(null, clickedCategory, clickedSeries); // 假设函数已定义
            }
        });

    } catch (error) {
        console.error('获取柱状图数据失败', error);
    }
}


async function updatePieChart() {
    try {
        // 从后端接口获取数据
        const response = await axios.get('/api/categorize'); // 假设接口地址是 /api/categorize
        const resData = response.data;

        // 检查后端响应是否正确
        if (resData.code !== 200 || !resData.data) {
            console.error('后端返回错误或无有效数据');
            return;
        }

        // 提取后端返回的数据
        const chartData = resData.data.map(item => ({
            value: item.value,
            name: item.name
        }));

        // 配置 ECharts 图表选项
// 配置 ECharts 图表选项
        const option = {
            title: {
                left: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} ({d}%)' // 鼠标悬停时显示分类、值和百分比
            },
            legend: {
                show: false // 隐藏图例
            },
            series: [
                {
                    name: '分类统计',
                    type: 'pie',
                    radius: ['30%', '70%'], // 设置内外半径，让饼图更大
                    data: chartData, // 动态数据
                    label: {
                        show: true, // 显示每个分割的标签
                        position: 'outside', // 标签位置在饼图外部
                        formatter: '{b}: {d}%' // 标签格式，显示分类名称和百分比
                    },
                    labelLine: {
                        show: true // 显示标签连接线
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };


        // 初始化 ECharts 实例
        const chartDom = document.getElementById('pie');
        const myChart = echarts.init(chartDom);

        // 使用新配置更新图表
        myChart.setOption(option);

        // 绑定点击事件
        myChart.on('click', function (params) {
            console.log(`Clicked category: ${params.name}`); // 调试输出
            updateArticleList(params.name); // 点击分类后更新文章列表
        });

    } catch (error) {
        console.error('加载饼图数据失败:', error);
    }
}


// 更新混合图事件
async function updateMixChart() {
    try {
        const response = await axios.get('/api/read');
        const data = response.data.data;

        // 检查后端响应是否正确
        if (!data || !data.labels || !data.counts || !data.reads) {
            console.error('后端返回错误或无有效数据');
            return;
        }

        // 配置 ECharts 图表选项
        const option = {
            color: ['#3E82F7', '#F86C6B'], // 使用新的配色
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow' // 阴影指示器
                }
            },
            legend: {
                data: ['文章数', '阅读量'],
                textStyle: {
                    color: '#333' // 图例文字颜色
                }
            },
            grid: {
                top: '10%',
                bottom: '25%', // 为 90° 旋转标签预留更多空间
                right: '10%'
            },
            xAxis: [
                {
                    type: 'category',
                    axisTick: {
                        alignWithLabel: true
                    },
                    axisLabel: {
                        rotate: 90, // 旋转 90°，垂直显示
                        interval: 0, // 显示所有标签
                        formatter: function (value) {
                            // 长文本换行
                            return value.length > 15
                                ? value.substring(0, 15) + '\n' + value.substring(10)
                                : value;
                        },
                        textStyle: {
                            fontSize: 10, // 字体大小
                            color: '#333', // 标签字体颜色
                            // fontWeight: 'bold' // 字体加粗
                        }
                    },
                    data: data.labels // 使用后端返回的标签
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    name: '文章数',
                    position: 'left',
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: '#3E82F7'
                        }
                    },
                    axisLabel: {
                        formatter: '{value}'
                    },
                    splitLine: {
                        lineStyle: {
                            type: 'dashed',
                            color: '#DDD'
                        }
                    }
                },
                {
                    type: 'value',
                    name: '阅读量',
                    position: 'right',
                    alignTicks: true,
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: '#F86C6B'
                        }
                    },
                    axisLabel: {
                        formatter: '{value}'
                    },
                    splitLine: {
                        show: false // 不显示右侧 Y 轴的辅助线
                    }
                }
            ],
            series: [
                {
                    name: '文章数',
                    type: 'bar',
                    data: data.counts, // 使用后端返回的文章数
                    yAxisIndex: 0,
                    barWidth: '40%',
                    itemStyle: {
                        color: '#3E82F7',
                        barBorderRadius: [4, 4, 0, 0]
                    }
                },
                {
                    name: '阅读量',
                    type: 'line',
                    data: data.reads, // 使用后端返回的阅读量
                    yAxisIndex: 1,
                    smooth: true,
                    lineStyle: {
                        color: '#F86C6B',
                        width: 3
                    },
                    itemStyle: {
                        color: '#F86C6B'
                    }
                }
            ]
        };

        // 渲染 ECharts 图表
        const chart = echarts.init(document.getElementById('mix'));
        chart.setOption(option);

        // 绑定点击事件
        chart.on('click', function (params) {
            if (params && params.name) {
                const clickedType = params.name;
                console.log(`Clicked type: ${clickedType}`); // 调试输出
                updateArticleList(clickedType); // 调用更新函数
            }
        });

    } catch (error) {
        console.error('获取混合图数据失败', error);
    }
}

async function updateHeatmap() {
    const year = document.getElementById('yearSelect').value;

    try {
        // 从后端接口获取数据
        const response = await axios.get(`/api/heatmap/${year}`);
        const resData = response.data;

        // 检查后端响应是否正确
        if (resData.code !== 200 || !resData.data) {
            console.error('后端返回错误或无有效数据');
            return;
        }

        console.log(resData); // 调试输出，查看后端返回的数据

        // 提取后端返回的数据
        const heatmapData = resData.data.data; // 热力图数据
        const xAxisData = resData.data.xAxis; // X 轴数据（周数）
        const yAxisData = resData.data.yAxis; // Y 轴数据（星期）

        // 自定义颜色比例，从浅色到深色，更明显地区分数据强度
        const colorScale = [
            [0, '#f7fbff'],     // 极浅蓝，几乎没有文章
            [0.2, '#c6dbef'],   // 浅蓝，很少文章
            [0.4, '#6baed6'],   // 中等蓝，适度写作
            [0.6, '#3182bd'],   // 深蓝，高强度写作
            [1, '#08519c']      // 浓深蓝，非常高的写作强度
        ];


        // 配置 ECharts 图表选项
        const option = {
            tooltip: {
                position: 'top',
                formatter: function (params) {
                    return `周数: ${xAxisData[params.value[0]]}<br>星期: ${yAxisData[params.value[1]]}`;
                }
            },
            grid: {
                height: '70%', // 调整图表网格高度
                width: '75%',  // 调整宽度，留出右侧空间用于 visualMap
                top: '10%',    // 图表顶部间距
                left: '10%'    // 图表左侧间距
            },
            xAxis: {
                type: 'category',
                data: xAxisData, // X 轴数据（周数）
                splitArea: {
                    show: true, // 显示网格分隔区域
                    lineStyle: {
                        width: 1,
                        type: 'dashed',
                        color: '#1b1919' // 设置分隔线颜色
                    },
                    areaStyle: {
                        color: ['#beb4b4', '#dccfcf'] // 网格背景交替颜色
                    }
                },
                axisLabel: {
                    fontSize: 14, // 加大字体
                    rotate: 45    // 旋转标签，避免重叠
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#aaa' // 设置坐标轴颜色
                    }
                }
            },
            yAxis: {
                type: 'category',
                data: yAxisData, // Y 轴数据（星期）
                splitArea: {
                    show: true, // 显示网格分隔区域
                    lineStyle: {
                        width: 1,
                        type: 'dashed',
                        color: '#1b1a1a' // 设置分隔线颜色
                    },
                    areaStyle: {
                        color: ['#f9f9f9', '#ffffff'] // 网格背景交替颜色
                    }
                },
                axisLabel: {
                    fontSize: 14 // 加大字体
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: '#aaa' // 设置坐标轴颜色
                    }
                }
            },
            visualMap: {
                min: 0,
                max: Math.max(...heatmapData.map(item => item[2])), // 动态设置最大值
                calculable: true,
                orient: 'vertical', // 设置为垂直方向
                right: '5%',        // 设置在图表右侧
                top: 'middle',      // 垂直居中显示
                inRange: {
                    color: colorScale.map(item => item[1]) // 应用自定义颜色比例
                },
                textStyle: {
                    fontSize: 12 // 调整字体大小
                }
            },
            series: [
                {
                    name: '文章发布热力图',
                    type: 'heatmap',
                    data: heatmapData, // 热力图数据
                    label: {
                        show: false // 隐藏标签，按照颜色强度表示数据
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };

        // 渲染 ECharts 图表
        const chart = echarts.init(document.getElementById('heatmap'));
        chart.setOption(option);

    } catch (error) {
        console.error('数据请求失败:', error);
    }
}


async function updateArticleList(filterType = null, filterYear = null, fileQuarter = null) {
    const params = new URLSearchParams();

    // 根据筛选条件添加查询参数
    if (filterType) {
        console.log(`Filtering by type: ${filterType}`); // 调试输出
        params.append('type', filterType);
    }

    if (filterYear) {
        console.log(`Filtering by month: ${filterYear}`); // 调试输出
        params.append('year', filterYear);
    }
    if (fileQuarter) {
        console.log(`Filtering by quarter: ${fileQuarter}`); // 调试输出
        params.append('quarter', fileQuarter);
    }

    try {
        // 异步获取文章数据
        const response = await axios.get('/api/articles?' + params.toString());
        const resData = response.data;
        console.log('Response:', resData);
        // 检查后端响应是否正确
        if (resData.code !== 200 || !resData.data) {
            console.error('后端返回错误或无有效数据');
            return;
        }
        const articles = resData.data;
        console.log('Articles:', articles); // 调试输出
        // 动态生成 HTML 表格
        const tableHtml = `
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 12px;">
                <thead>
                    <tr style="background-color: #f9f9f9; font-size: 14px; font-weight: bold;">
                        <th style="padding: 8px; border-bottom: 2px solid #ddd;">标题</th>
                        <th style="padding: 8px; border-bottom: 2px solid #ddd;">类型</th>
                        <th style="padding: 8px; border-bottom: 2px solid #ddd;">日期</th>
                    </tr>
                </thead>
                <tbody>
                    ${
            articles.map(article => `
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px;">
                                    <a href="${article.url}" target="_blank" style="text-decoration: none; color: #007bff; font-size: 14px; font-weight: 500;">${article.title}</a>
                                </td>
                                <td style="padding: 8px; font-size: 12px; color: #333;">${article.type}</td>
                                <td style="padding: 8px; font-size: 12px; color: #666;">${article.date}</td>
                            </tr>
                        `).join('')
        }
                </tbody>
            </table>
        `;

        // 更新文章列表的 HTML
        document.getElementById('articleList').innerHTML = tableHtml;
    } catch (error) {
        console.error('获取文章列表出错:', error);
        document.getElementById('articleList').innerHTML = '<p style="color: red;">加载文章列表失败，请稍后重试。</p>';
    }
}


// 事件监听器
document.getElementById('yearSelect').addEventListener('change', updateHeatmap);
// 获取 select 和标题元素
const yearSelect = document.getElementById('yearSelect');
const chartTitle = document.getElementById('chartTitle');

// 添加事件监听，当用户选择年份时更新标题
yearSelect.addEventListener('change', function () {
    const selectedYear = yearSelect.value; // 获取用户选择的年份
    chartTitle.textContent = `${selectedYear} 年 写作发布热力图`; // 更新标题内容
});

// 初始化
document.addEventListener('DOMContentLoaded', initCharts);

// 定时刷新（每分钟）
setInterval(initCharts, 60000);