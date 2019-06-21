% Josué Pagán. 29/05/2019
close all
% eda=csvread('/home/josueportiz/Drive/data/piloto_2018-19/MG0319029/basals/raw_20190121/Dataexport/EDA.csv');
% acc=csvread('/home/josueportiz/Drive/data/piloto_2018-19/MG0319029/basals/raw_20190121/Dataexport/ACC.csv');

eda=csvread('/home/josueportiz/Drive/Docencia/TFXs/alumnos/2019-miguelMerino-TFM/data/ejemplos/ejemplo1/EDA.csv');
acc=csvread('/home/josueportiz/Drive/Docencia/TFXs/alumnos/2019-miguelMerino-TFM/data/ejemplos/ejemplo1/ACC.csv');

fsEda = eda(2);
fsAcc = acc(2,1);

eda = eda(3:end,:);
acc = acc(3:end,:)/64;
Eacc = sqrt(sum(acc.^2,2));

figure(1)
subplot(211); plot(eda);
subplot(212); plot(Eacc);

% Vars:
thstdEDA = 0.5;
thstdX = 0.1;
thstdY = 0.1;
thstdZ = 0.1;
thstdE = 0.1;

%% Compute std for different windows
winLenSec = [0.5, 1, 2, 5, 10];


for s = 1 : length(winLenSec)
    numWins = floor(min(length(eda)/fsEda, size(acc, 1)/fsAcc)/winLenSec(s));
    corrMatX = zeros(numWins, 2);
    corrMatY = zeros(numWins, 2);
    corrMatZ = zeros(numWins, 2);
    corrMatE = zeros(numWins, 2);
    edaWindowed = eda;
    EaccWindowed = Eacc;
    
    for w = 1 : numWins
        edaWin = fsEda * winLenSec(s)*(w-1)+1 : fsEda * winLenSec(s)*w;
        accWin = fsAcc * winLenSec(s)*(w-1)+1 : fsAcc * winLenSec(s)*w;
        
        corrMatX(w, 1) = std(eda(edaWin));
        corrMatY(w, 1) = std(eda(edaWin));
        corrMatZ(w, 1) = std(eda(edaWin));
        corrMatE(w, 1) = std(eda(edaWin));
        corrMatX(w, 2) = std(acc(accWin, 1));
        corrMatY(w, 2) = std(acc(accWin, 2));
        corrMatZ(w, 2) = std(acc(accWin, 3));
        corrMatE(w, 2) = std(Eacc(accWin));    
    
        %% Thresholding    
        edaWindowed((corrMatE(w, 1) < thstdEDA) && (corrMatE(w, 2) < thstdE)) = 1;
        EaccWindowed((corrMatE(w, 1) < thstdEDA) && (corrMatE(w, 2) < thstdE)) = 1;
    end
    
    corrMatX(corrMatX(:, 1) < thstdEDA, :) = [];
    corrMatY(corrMatY(:, 1) < thstdEDA, :) = [];
    corrMatZ(corrMatZ(:, 1) < thstdEDA, :) = [];
    corrMatE(corrMatE(:, 1) < thstdEDA, :) = [];
    
    corrMatX(corrMatX(:, 2) < thstdX, :) = [];
    corrMatY(corrMatY(:, 2) < thstdY, :) = [];
    corrMatZ(corrMatZ(:, 2) < thstdZ, :) = [];
    corrMatE(corrMatE(:, 2) < thstdE, :) = [];
    
    %% Plot signals
    figure(1)
    subplot(211); hold on; plot(eda(edaWindowed == 1), 'r')
    subplot(212); hold on; plot(Eacc(EaccWindowed ==1), 'r')
    
    %% Plot hist
    figure(2)
    subplot(length(winLenSec),5,5*(s-1)+1); histogram(corrMatX(:,1), 1000)
    xlim([0, 0.2])
    title(strcat('Win=',num2str(winLenSec(s)),' s. EDA'));
    ylabel('std(EDA)'); xlabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+2); histogram(corrMatX(:,2), 1000)
    xlim([0, 0.1])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccX'));
    ylabel('std(AccX)'); xlabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+3); histogram(corrMatY(:,2), 1000)
    xlim([0, 0.1])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccY'));
    ylabel('std(AccY)'); xlabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+4); histogram(corrMatZ(:,2), 1000)
    xlim([0, 0.1])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccZ'));
    ylabel('std(AccZ)'); xlabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+5); histogram(corrMatE(:,2), 1000)
    xlim([0, 0.1])
    title(strcat('Win=',num2str(winLenSec(s)),' s. EAcc'));
    ylabel('std(EAcc)'); xlabel('counts')
    
    %% Plot corrs
    figure(3)
    
    % X
    subplot(length(winLenSec),4,4*(s-1)+1); scatter(corrMatX(:,1), corrMatX(:,2), 'b+')
    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMatX(:,1), corrMatX(:,2));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    ylabel('std(AccX)')
    xlabel('std(EDA)')
    
    % Y
    subplot(length(winLenSec),4,4*(s-1)+2); scatter(corrMatY(:,1), corrMatY(:,2), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMatY(:,1), corrMatY(:,2));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    ylabel('std(AccY)')
    xlabel('std(EDA)')
    
    % Z
    subplot(length(winLenSec),4,4*(s-1)+3); scatter(corrMatZ(:,1), corrMatZ(:,2), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMatZ(:,1), corrMatZ(:,2));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    ylabel('std(AccZ)')
    xlabel('std(EDA)')
    
    % Eacc
    subplot(length(winLenSec),4,4*(s-1)+4); scatter(corrMatE(:,1), corrMatE(:,2), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMatE(:,1), corrMatE(:,2));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    ylabel('std(EAcc)')
    xlabel('std(EDA)')
end

