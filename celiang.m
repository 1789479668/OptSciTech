% data = load('store.mat');


y = imgaussfilt(mean(cdata(400:800,:),1),3);
    % 基线校准
%     y= dtrend(y,0);
    %找峰值,最小峰值   12在22.4~78.8，100浓度时设置为8
    [peak,peakloc] = findpeaks(y,"MinPeakHeight",8,"MinPeakDistance",50);
    %有小误差峰，但由于限制会筛选掉一大部分。然后再找到的峰内做减法，从最小的开始减小，保留一个主极大一个次级大。
    %不过当前参数好像都适用，如果不适用则可以再添加这个过程，可以添加一个限制，peak多于2个数据再筛选
    %这样就可以不改变第一、二峰顺序的情况下找到1、2峰
    while numel(peak) > 2
        % 找到数组中最小的值
        minValue = min(peak);
        % 找到最小值的索引
        minIndex = find(peak == minValue, 1);
        % 删除最小值
        peak(minIndex) = [];
    end
    %酒精峰
    peak_a = peak(2);
    %水峰
    peak_w = peak(1);

%     findpeaks(y,"MinPeakHeight",12,"MinPeakDistance",80,"MinPeakWidth",20);
    plot(y);
    hold on;
    % 获取比值
    bizhi = peak_a/peak_w;

    syms x;
%     f = 0.0002493*x^2-0.01025*x+1.046;%老曲线,在50%左右效果最好。
%     f = 0.0002571*x^2-0.006502*x+0.8466;%新曲线2，R2=0.996
%     f = 0.5339*exp(0.016*x);
%     if bizhi<=1.11
%         f = 0.4734*exp(0.0179*x);%30~40的拟合曲线
%     elseif 1.11<bizhi
%         f = 0.5037*exp(0.0163*x);
%     end
%     test1~4都是400~800区间使用的,test5~6是1~400区间使用，已经不适用了，由于硬件改变。
%     f = 0.5015*exp(0.0172*x);%test1，30~58之间，均误差0.618度，最大误差1.55，最小0.03
%     f = 0.4738*exp(0.0183*x);%test2，30~62之间，均误差0.84度，最大误差2.01，最小0.16
%     f = 0.4973*exp(0.0174*x);%test3,30~60之间，均误差0.556度，最大误差1.5，最小误差0
%     f = 0.4926*exp(0.0175*x);%test4,30~60之间，均误差0.5665度，最大误差1.33，最小误差0.14
%
%     f = 0.5295*exp(0.0164*x);%test5，30~60之间，均误差0.576，最大误差1.3,最小0.03。
%     f = 0.5095*exp(0.0171*x);%test6,30~60之间，均误差0.661，最大误差1.46，最小误差0。

%   test7,test8是准确标定，400~800.test9和test10是主办方仪器标定，400~800
%     f = 0.4617*exp(0.0189*x);%test7e,
%     f = 0.4532*exp(0.0193*x);%test8e,效果更好！
%     f = 0.4262*exp(0.0224*x);%test9e,
%   test11准确标定，400-800；test12仪器标定，400-800
%     f = 0.4529*exp(0.0203*x);%test11
    f = 0.4336*exp(0.0229*x);%test12
    x = solve(f==bizhi);
    x = vpa(x,4);