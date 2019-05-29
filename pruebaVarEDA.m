% Josué Pagán. 29/05/2019

eda=csvread('/home/josueportiz/Drive/data/piloto_2018-19/MG0319029/basals/raw_20190121/Dataexport/EDA.csv');
acc=csvread('/home/josueportiz/Drive/data/piloto_2018-19/MG0319029/basals/raw_20190121/Dataexport/ACC.csv');

fsEda = eda(2);
fsAcc = acc(2,1);

eda = eda(3:end,:);
acc = acc(3:end,:)/64;
Eacc = sqrt(sum(acc.^2,2));

figure(1)
subplot(211); plot(eda);
subplot(212); plot(Eacc);

%% Compute std for different windows
winLenSec = [0.5 1, 2, 5, 10, 30];


for s = 1 : length(winLenSec)
    numWins = floor(min(length(eda)/fsEda, size(acc, 1)/fsAcc)/winLenSec(s));
    corrMat = zeros(numWins, 5);
    
    for w = 1 : numWins
        corrMat(w, 1) = std(eda(fsEda * winLenSec(s)*(w-1)+1 :...
            fsEda * winLenSec(s)*w));
        corrMat(w, 2) = std(acc(fsAcc * winLenSec(s)*(w-1)+1 :...
            fsAcc * winLenSec(s)*w, 1));
        corrMat(w, 3) = std(acc(fsAcc * winLenSec(s)*(w-1)+1 :...
            fsAcc * winLenSec(s)*w, 2));
        corrMat(w, 4) = std(acc(fsAcc * winLenSec(s)*(w-1)+1 :...
            fsAcc * winLenSec(s)*w, 3));
        corrMat(w, 5) = std(Eacc(fsAcc * winLenSec(s)*(w-1)+1 :...
            fsAcc * winLenSec(s)*w));    
    end
    
    %% Plot hist
    figure(2)
    subplot(length(winLenSec),5,5*(s-1)+1); histogram(corrMat(:,1), 1000)
    xlim([0, 0.5])
    title(strcat('Win=',num2str(winLenSec(s)),' s. EDA'));
    xlabel('std(EDA)'); ylabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+2); histogram(corrMat(:,2), 1000)
    xlim([0, 0.5])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccX'));
    xlabel('std(AccX)'); ylabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+3); histogram(corrMat(:,3), 1000)
    xlim([0, 0.5])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccY'));
    xlabel('std(AccY)'); ylabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+4); histogram(corrMat(:,4), 1000)
    xlim([0, 0.5])
    title(strcat('Win=',num2str(winLenSec(s)),' s. AccZ'));
    xlabel('std(AccZ)'); ylabel('counts')
    
    subplot(length(winLenSec),5,5*(s-1)+5); histogram(corrMat(:,5), 1000)
    xlim([0, 0.5])
    title(strcat('Win=',num2str(winLenSec(s)),' s. EAcc'));
    xlabel('std(EAcc)'); ylabel('counts')
    
    %% Plot corrs
    figure(3)
    
    % X
    subplot(length(winLenSec),4,4*(s-1)+1); scatter(corrMat(:,1), corrMat(:,2), 'b+')
    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMat(:,1), corrMat(:,2));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    xlabel('std(AccX)')
    ylabel('std(EDA)')
    
    % Y
    subplot(length(winLenSec),4,4*(s-1)+2); scatter(corrMat(:,1), corrMat(:,3), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMat(:,1), corrMat(:,3));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    xlabel('std(AccY)')
    ylabel('std(EDA)')
    
    % Z
    subplot(length(winLenSec),4,4*(s-1)+3); scatter(corrMat(:,1), corrMat(:,4), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMat(:,1), corrMat(:,4));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    xlabel('std(AccZ)')
    ylabel('std(EDA)')
    
    % Eacc
    subplot(length(winLenSec),4,4*(s-1)+4); scatter(corrMat(:,1), corrMat(:,5), 'b+')    
    hold on; l = lsline; set(l, 'LineWidth', 2)
    
    R = corrcoef(corrMat(:,1), corrMat(:,5));
    Rsq = R(1,2).^2;
    
    title(strcat('Win=',num2str(winLenSec(s)),' s. R^2=',num2str(Rsq)));
    xlabel('std(EAcc)')
    ylabel('std(EDA)')
end

