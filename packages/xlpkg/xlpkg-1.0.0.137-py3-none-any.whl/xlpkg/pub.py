class Css():
        css00 = 'background-color:lightblue;    color:green;    font:bold italic large /"Times New Roman/";font-size:12px;'
        css01 = 'background-color:lightblue;    color:gray;     font:bold italic large /"Times New Roman/";font-size:12px;'
        css02 = 'background-color:lightblue;    color:pink;'
        css03 = 'background-color:green;        color:white'
        css04 = "QHeaderView::section {background-color: #f0f0f0; color: black;}"
        css05 = "QHeaderView::section {background-color: lightblue; color: black;}"
        css06 = "QHeaderView::section {background-color: lightgreen; color: black;}"
        css07 = 'background-color:lightblue;'
        css08 = 'background-color:pink;        color:white'
        css09 = 'background-color:pink;        color:black'
        css10 = 'background-color:pink;        color:red'

        css11 = 'background-color:green;        color:white'
        css12 = 'background-color:green;        color:black'
        css13 = 'background-color:green;        color:red'
        css14 = 'background-color:green;        color:blue'
        css15 = 'background-color:green;        color:orange'
        css16 = 'background-color:green;        color:pink'
        css17 = 'background-color:green;        color:lightgray'
        css21 = 'background-color:green;        color:lightwhite'
        css22 = 'background-color:green;        color:lightblack'
        css23 = 'background-color:green;        color:lightred'
        css24 = 'background-color:green;        color:lightblue'
        css25 = 'background-color:green;        color:lightorange'
        css26 = 'background-color:green;        color:lightpink'
        css27 = 'background-color:green;        color:lightgray'
        pass
#与types相同
products=(
        ('all','全部'),
        ('15','跑腿快车'),
        ('16','快车超市'),
        ('18','快车代驾'),
        ('20','客服问题'),
        ('!20','非客服问题'))
groups=(
        ('all',     '全部'),
        ('devel',   '开发'),
        ('test',    '测试'),
        ('design',  '产品'),
        ('check',   '验收'),
        ('ui',      'UI'))
groups_bug=(
        ('all',     '全部'),
        ('test',   '测试'),
        ('kf',      '客服'))
#与groups相同
types=(
        ('all','    全部'),
        ('devel',   '开发'),
        ('test',    '测试'),
        ('design',  '产品'),
        ('check',   '验收'),
        ('ui',      'UI'))

names_all=(
        ('all','全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',          '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉'), 
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波'),
        ('- - - -','- - - -'), 
        ('xiongqi',         '熊琪' ), 
        ('xiaolong',        '肖龙'), 
        ('huanglifei',      '黄麗妃'), 
        ('liuyifei',        '刘怡妃') ,
        ('gongcandong',     '龚灿东'), 
        ('huangfengming',   '黄凤明'), 
        ('wangechen',       '王郴')) 

names_test=(
        ('all',             '全部'), 
        ('xiongqi',         '熊琪' ), 
        ('xiaolong',        '肖龙'), 
        ('huanglifei',      '黄麗妃'), 
        ('liuyifei',        '刘怡妃')) 
names_devel=(
        ('all',             '全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',         '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉'), 
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波') 
        )

names_design=(
        ('all',             '全部'), 
        ('gongcandong',     '龚灿东'), 
        ('huangfengming',   '黄凤明'))
names_front=(
        ('all',             '全部'),
        ('liuchengjie',     '刘成杰'), 
        ('huanglinqiang',   '黄林强'), 
        ('wangjun',         '王军'), 
        ('jiangjiapei',     '江佳沛'), 
        ('huangligen',      '黄立根'), 
        ('luyonghui',       '卢永辉')
        )

names_background=(
        ('all',             '全部'),
        ('liudong',         '刘东'), 
        ('liuyunlong' ,     '刘允隆'),
        ('guoweihong',      '郭伟红'),
        ('litulong',        '李土龙'), 
        ('luojianbo',       '罗剑波') 
        )
names_ui=(
        ('all',             '全部'), 
        ('wangchen',        '王郴'))
names_kf=(
        ('all',             '全部'), 
        ('liaojianbing',    '廖健兵'),
        ('yanliren',        '杨莉仁'),
        ('xiaolong',        '肖龙')
        )
names_ops=(
        ('all','全部'),
        ('liangyuqi',       '梁玉琦'),
        ('xieliangbin',     '谢亮斌'))

status_bug=(
        ('all',             '全部'),
        ('active',          '激活'),
        ('resolved',        '已解决'),
        ('closed',          '已关闭')
        )
status_task=(
        ('all',             '全部'),
        ('pause',           '暂停'  ), 
        ('wait',            '准备中' ), 
        ('doing',           '进行中' ), 
        ('closed',          '已关闭' ), 
        ('done',            '已完成'),
        ('!done',           '未完成'))

#task
time_task=( 
        ('openedDate',      '创建时间'),
        ('assignedDate',    '指派时间'),
        ('realStarted',     '开始时间'),
        ('closedDate',      '完成时间'))

titles_task=(
        ('0','产品'),
        ('1','需求ID'),
        ('2','任务ID'),
        ('3','需求'),
        ('4','任务名称'),
        ('5','小组'),
        ('6','责任人'),
        ('7','状态'),
        ('8','测试完成'),
        ('9','冲刺'),
        ('10','上预发布'),
        ('11','测试环境'),
        ('12','测试完成'),
        ('13','验收环境'),
        ('14','验收完成'))

titles_buglist=( 
        ('0','Product'),
        ('1','BugID'),
        ('2','Bug标题'),
        ('3','严重程度'),
        ('4','优先级'),
        ('5','创建时间'),
        ('6','关闭时间'),
        ('7','创建人'),
        ('8','指派给'),
        ('9','状态'))

titles_bugtj1=( 
        ('0','Product'),
        ('1','严重程度'),
        ('2','数量'))

titles_bugtj2=( 
        ('0','Product'),
        ('1','严重程度'),
        ('2','状态'),
        ('3','数量'))

task_p=( 
        ('10','10行'),
        ('20','20行'),
        ('50','50行'),
        ('100','100行'),
        ('200','200行'))

#bug
bug_titles=( 
        ('0','Product'),
        ('1','BugID'),
        ('2','Bug标题'),
        ('3','严重程度'),
        ('4','优先级'),
        ('5','创建人'),
        ('6','状态'))
bug_p=( 
        ('0','10'),
        ('1','20'),
        ('2','50'),
        ('3','100'),
        ('4','200')
        )

#kf
kf_names=(
        ('0','全部'),
        ('1','波'),
        ('2','隆'),
        ('3','龙'),
        ('4','红'),
        ('5','刘东'),
        ('6','黄麗妃'),
        ('7','龚灿东'))
kf_types=( 
        ('0','创建时间'),
        ('1','指派时间'),
        ('2','解决时间'),
        ('3','关闭时间')
        )

kf_stas=( 
        ('0','全部',), 
        ('2','激活',), 
        ('3','已解决',), 
        ('4','已关闭',)
        )
kf_titles=( 
        ('0','产品名称'),
        ('1','模块名称'),
        ('2','问题编号'),
        ('3','问题描述'),
        ('4','严重程度'),
        ('5','优先级'),
        ('6','提交人'),
        ('7','创建时间'),
        ('8','解决时间'),
        ('8','关闭时间'),
        ('9','状态')
        )
kf_p=( 
        ('0','10'),
        ('1','20'),
        ('2','50'),
        ('3','100'),
        ('4','200'))

kfcx_titles=(
        ('0','代理商ID'),
        ('1','商家ID'),
        ('2','商家名称'),
        ('3','商家电话'),
        ('4','商家地址'),
        ('5','订单编号'),
        ('6','订单类型'),
        ('7','抽成方式'),
        ('8','订单状态'),
        
        ('9','取消状态'),('10','退款状态'))
kfcxprinter_titles=(
        ('0','代理商ID'),
        ('1','代理商名称'),
        ('2','商家ID'),
        ('3','商家名称'),
        ('4','商家电话'),
        ('5','外卖电话'),
        ('6','商家地址'),
        ('7','statu'),
        ('8','status'),
        ('9','statusx'),
        ('10','自动标签打印'),
        ('11','是否删除'),
        ('12','是否代理商删除'))
titles_fyinfo=(
        ('0','平台编码'), 
        ('1','代理商id'), 
        ('2','代理商名称'), 
        ('3','商家id'), 
        ('4','商家名称'), 
        ('5','商家联系电话'), 
        ('6','第三方类型'), 
        ('7','入账方主体类型'), 
        ('8','到账周期类型'), 
        ('9','最后申请日期'), 
        ('10','入账账户类型'), 
        ('11','入账商家名称'), 
        ('12','入账方类型'), 
        ('13','入账证件到期日'), 
        ('14','入账方主体名称'), 
        ('15','入账卡号'), 
        ('16','入账卡用户名称'), 
        ('17','入账卡银行预留手机号'), 
        ('18','入账卡开户行名称'), 
        ('19','开户许可证照片地址'), 
        ('20','开户行行号'), 
        ('21','开户证件类型'), 
        ('22','开户证件名称'), 
        ('23','开办资金'), 
        ('24','开户证件代码'), 
        ('25','开户证件有效期'), 
        ('26','证件扫码图片地址'), 
        ('27','品牌名称') , 
        ('28','电子邮件' ), 
        ('29','联系人名称'), 
        ('30','联系人电话'), 
        ('31','证件号'), 
        ('32','证件到期日'), 
        ('33','证件类型'), 
        ('34','身份证正面照片'), 
        ('35','身份证反面照片'), 
        ('36','分账合同名称'), 
        ('37','合同开始时间'), 
        ('38','合同到期时间'), 
        ('38','合同照片路径'), 
        ('40','合同最大分成比例'), 
        ('41','入账方的商户编号'), 
        ('42','入账方合同编号'), 
        ('43','入账合同规则'), 
        ('44','最后申请状态'), 
        ('45','创建时间'), 
        ('46','更新时间'))

help_sms={"01":"/ /help  接口用法帮助","/sms?m=15975576669":"根据手机号码查询短信验证码"}



