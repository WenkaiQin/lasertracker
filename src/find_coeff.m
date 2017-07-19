N = 4;
u = [0.3 0.4 0.3];
uo = [0.3 0.4 0.3];

for i = 1:N
    u = conv(u, uo);
end

disp(u)