function draw_ast(mydom){

console.log(mydom);
var textarea = mydom.parent().next().find('div#leave-message-textarea');
var pre_code = mydom.parent().next().find('code');
var pre_rst = mydom.parent().parent().next().find('pre');
pre_rst.html('<div class="ast_container" style="height: 500px;"></div>')
var parent_id = mydom.parent().parent().parent().attr("id");
// console.log(pre_rst)
var this_code = textarea.text();
pre_code.text(textarea.text());
console.log(this_code);

var dom = pre_rst.find('div.ast_container').get()[0];
console.log(dom);
var myChart = echarts.init(dom);
console.log(dom);
var app = {};
option = null;
myChart.showLoading();
$.post("/getAST",{code:this_code}, function (data) {

    // console.log(data);
    myChart.hideLoading();

    echarts.util.each(data.children, function (datum, index) {
        // index % 2 === 0 && (datum.collapsed = true);
        // datum.collapsed = true
    });
    // console.log(data);

    myChart.setOption(option = {
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [
            {
                type: 'tree',

                data: [data],

                // top: '1%',
                // left: '7%',
                // bottom: '1%',
                // right: '20%',

                symbolSize: 7,

                label: {
                    position: 'left',
                    verticalAlign: 'middle',
                    align: 'right',
                    fontSize: 9
                },

                leaves: {
                    label: {
                        position: 'right',
                        verticalAlign: 'middle',
                        align: 'left'
                    }
                },

                expandAndCollapse: true,
                animationDuration: 550,
                animationDurationUpdate: 750
            }
        ]
    });
});
}