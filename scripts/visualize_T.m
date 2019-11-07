data = csvread('../work/device_parameters.csv');

resx = data(1,1);%100.000 130.000 68.000
resy = data(1,2);
resz = data(1,3);

l = data(2,1)/resx;%15;96 108 28
w = data(2,2)/resy;% 9;
h = data(2,3)/resz;%10;

T = csvread('../work/T.out');
T_n = zeros(l,w,h);
i = 1;

for z = 1:h
    for y = 1:w
        for x = 1:l
            T_n(x,y,z) = T(i);
            X(i) = x;
            Y(i) = y;
            Z(i) = z;
            i =i+1;
        end
    end
end

%Ploting temperature at eachs location
x_new = repmat(1:  w,  l, 1,  h);
y_new = repmat((1:  l)',1,  w,  h);
z_new = repmat(reshape(1:  h,1,1,  h),  l,  w,1);
f1 = figure;
colormap(jet(256));


% Create axes

%codediagram=slice(x_new, y_new, z_new, T,[1 2 ], [1 2 ], 0:k_ran);
%diagram=slice(x_new, y_new, z_new, T,[  i_ran/2-1,   i_ran/2+1,   i_ran/2+ 3 ], [  j_ran/2 ], [55, 0.56*  k_ran-20:4:0.56*  k_ran+5,110]);%k_ran);
%diagram=slice(x_new, y_new, z_new, T,[(  j_ran)/2], [(  i_ran)/3 ], [  face]);%k_ran);
diagram=slice(x_new, y_new, z_new, T_n(:,:,:),[w/3, w/2, 2*w/3], [l/2], [h/5,2*h/5,3*h/5,4*h/5,4*h/5]);%k_ran);

xlabel('width')
ylabel('length')
zlabel('hieght')
disp("Plotting the temperature profile...")
cb = colorbar;
cb.Label.String = "Temperature rise (K)";
colormap(jet(256));
saveas(f1, '../output/temperature_profile.png');
%exit();

figure1 = figure;
diagram=slice(x_new, y_new, z_new, T_n(:,:,:),[], [l/2], []);%k_ran);

xlabel('width')
ylabel('length')
zlabel('hieght')
disp("Plotting the temperature profile...")
cb = colorbar;
cb.Label.String = "Temperature rise (K)";
colormap(jet(256));
view(0,0)
set(diagram,'edgecolor','none')

% Create rectangle
annotation(figure1,'rectangle',...
    [0.285210526315789 0.346246973365617 0.0674210526315789 0.150121065375303],...
    'LineWidth',3,...
    'LineStyle','--');

% Create rectangle
annotation(figure1,'rectangle',...
    [0.574684210526316 0.343825665859564 0.0639122807017544 0.152542372881356],...
    'LineWidth',3,...
    'LineStyle','--');

% Create textarrow
annotation(figure1,'textarrow',[0.429824561403509 0.357894736842105],...
    [0.611590799031477 0.498789346246973],'String',{'Fins'},'FontSize',14);

% Create arrow
annotation(figure1,'arrow',[0.510526315789474 0.580701754385965],...
    [0.605326876513317 0.491525423728814]);

% Create textbox
annotation(figure1,'textbox',...
    [0.135087719298246 0.239709443099274 0.635087719298246 0.101694915254237],...
    'String','                        SOI Box',...
    'LineWidth',3,...
    'LineStyle','--',...
    'FontSize',14,...
    'FitBoxToText','off');

% Create textbox
annotation(figure1,'textbox',...
    [0.135087719298246 0.121065375302663 0.635087719298246 0.11864406779661],...
    'Color',[1 1 1],...
    'String','                     Si Substrate',...
    'LineWidth',3,...
    'LineStyle','--',...
    'FontSize',14,...
    'FitBoxToText','off');


saveas(figure1, '../output/temperature_profile_cross_section.png');
%exit();



