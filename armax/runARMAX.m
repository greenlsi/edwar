function runARMAX(varargin)
    dbstop at 8
    %     dbstop at 29
    %dbstop at 442
    
    
    %% CONSTANTS
    METRIC = 'mse';
    df_MNOI = str2double(getenv('df_MAX_NUMBER_OF_INPUTS'));
    target = getenv('dftarget');

    %% PARSE INPUTS
    mode = varargin{1};
    inputDir = varargin{2};
    outputDir = varargin{3};
    algorithm = varargin{4};
    
    %% CREATE OR VALIDATE MODEL
    switch mode
        case 'create' % Create a new model from data
            reportFile = strcat('log_Models', upper(algorithm),'.txt');
                        
            nx = varargin{5}; % The model's orders
            opts = varargin{6};
            norm = varargin{7}; % Normalize data or not (TRUE or FALSE)
            dataInfo = varargin{8}; % 4 elements vector: Time, NOT frequency, Units, storageRate, fs
            inNames = varargin{9};
            outName = varargin{10}; % To compare with
            
            % Create the model
            [model, dataRead, orders] = ...
                createARMAXModel(nx, opts, norm, dataInfo, inNames, outName); % Call function
            if ~isempty(inNames)
                fileName = char(strcat('model_',...
                    sprintf('na%.0dnb%.0dnc%.0dnk%.0d',max(orders(:,1:size(dataRead.y,2))),...
                    max(orders(:,size(dataRead.y,2)+1:size(dataRead.u,2))),...
                    max(orders(:,size(dataRead.y,2)+size(dataRead.u,2)+1: 2*size(dataRead.y,2)+size(dataRead.u,2))),...
                    max(orders(:,2*size(dataRead.y,2)+size(dataRead.u,2)+1:2*size(dataRead.y,2)+2*size(dataRead.u,2)))),...
                    '_of_',...
                    cell2mat(cellfun(@(x) [x '_'], inNames, 'UniformOutput', false)), outName));
            else
                fileName = char(strcat('model_',...
                    sprintf('na%.0dnc%.0d',max(orders(:,1:size(dataRead.y,2))),...
                    max(orders(:,size(dataRead.y,2)+1:size(dataRead.u,2)))),...
                    '_of_',...
                    cell2mat(cellfun(@(x) [x '_'], inNames, 'UniformOutput', false)), outName));
            end
            
            
            % Save and print the results.
            % Compare model with the original output
            modelStruct = struct('stateSystem', model,...
                'goodness',0,...
                'orders',[],...
                'normalization', norm);
            saveModel(modelStruct, orders, dataRead, fileName);
        case 'validate' % Validate an existing model for data
            reportFile = strcat('log_Validation_Models', upper('ARMAX'),'.txt');
            
            modelDir = varargin{5};
            inNames = varargin{6};
            outName = varargin{7}; % To compare with
            
            % Validate the model
            [model, ~, predictedData] =...
                validateARMAXModel(modelDir, inNames, outName);
    end
    
    
    %% CREATE ARMAX MODEL
    function [stateSystem, data, orders] =...
            createARMAXModel(ordersModel, opt, normalization, domainInfo, predictorsNames, yName)
         % Load variables
        [predictors, ~, y,~, ~] =...
            loadVariables(inputDir, predictorsNames, yName, normalization);
        if size(predictors,2) ~= length(predictorsNames)
            predictorNamesString = cell2mat(cellfun(@(x) [x ', '], predictorsNames, 'UniformOutput', false));
            error('ErrorTests:convertTest', ...
                'Some of these predictors: %s do not exist in the directory:\n %s',...
                predictorNamesString, inputDir);
        elseif size(y,2) ~= length(yName)
            outputNamesString = cell2mat(cellfun(@(x) [x ', '], yName, 'UniformOutput', false));
            error('ErrorTests:convertTest', ...
                'The outputs: %s do not exist in the directory:\n %s',...
                outputNamesString, inputDir);
        end
        
   
        %%
        % Parse domain information vector
        domain = domainInfo{1}; % Time, NOT Frequency
        domainUnits = domainInfo{2}; % Secs, min...
        storageRate = str2double(domainInfo{3});
        fs = str2double(domainInfo{4});
        
        
        
        % Create a data object
        switch domain
            case 'Time'
                data = iddata(y, predictors, storageRate);
                data.TimeUnit = domainUnits;
            otherwise
                error('ErrorTests:convertTest', ...
                    'Domain must be ''Time'' NOT ''Frequency''');
        end
        
        data.una = predictorsNames;
        data.yna = yName;
        
        %% APPLY ARMAX ALGORITHM
        % Constants
        MIN_na = 2;
        MAX_na = 30;
        
        if ~isempty(predictorsNames)
            MAX_nb = 30;
        else
            MAX_nb = 0;
        end
        MIN_nb = MIN_na;
        INC_nb = 1;
        
        MAX_nc = 30;
        MIN_nc = 0;
        INC_nc = 5;
        
        MIN_nk = 0;
        INC_nk = 5;
        if ~isempty(predictorsNames)
            MAX_nk = 40;
        else
            MAX_nk = 0;
        end
        
        
        
        
        % If selected order is too big reduce it
        if strcmp(METRIC, 'fit') % METRIC: fit
            prevFit = 0;
        elseif strcmp(METRIC, 'mse')
            prevFit = Inf;
        end
        inputDelay = 0;
        ioDelay = 0;
        opt = armaxOptions('Focus', 'stability');
        switch algorithm
            case armax
                integrateNoise = false;
            case arimax
                integrateNoise = true;
        end
        % Init
        vuelta = 1;
        if 0
            vectorPointersnb = zeros(length(yName), length(predictorsNames));
            vectorPointersnk = zeros(length(yName), length(predictorsNames));
        end
        
        for na = MAX_na:-1:MIN_na
            switch target
                case 'migraine'
                    % Just one output, Ny = 1
                    na_ = na; % Ny-by-Ny matrix.
                otherwise
                    error('ErrorTests:convertTest', ...
                        'Bad target selected');
            end
            nb_ = repmat(na, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
            
            for nc = MAX_nc:-INC_nc:MIN_nc
                switch target
                    case 'migraine'
                        % Just one output, Ny = 1
                        nc_ = nc; % Ny-by-Ny matrix.
                    otherwise
                        error('ErrorTests:convertTest', ...
                            'Bad target selected');
                end
                nk_ = repmat(nc, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
                
                try
                    % TODO
                    fprintf('Vuelta:%d\nna:%d\nnb:%d\nnc:%d\nnk:%d\n\n', vuelta, na_, nb_(1), nc_, nk_(1))
                   
                    stateSystem = armax(data, [na_ nb_ nc_ nk_],...
                        'InputDelay', inputDelay,...
                        'ioDelay', ioDelay,...
                        'IntegrateNoise', integrateNoise, opt);
                    vuelta = vuelta + 1;
                    if strcmp(METRIC, 'fit') % METRIC: fit
                        [~, metricT, ~] = compare(data, stateSystem);
                        if metricT > prevFit
                            prevFit = metricT;
                            orders = [na_ nb_ nc_ nk_];
                        end
                    elseif strcmp(METRIC, 'mse')
                        yp = compare(data, stateSystem);
                        metricT = mean((data.y - yp.y).^2);
                        if metricT < prevFit
                            prevFit = metricT;
                            orders = [na_ nb_ nc_ nk_];
                        end
                    end
                catch E
                end
                % Update vector of pointers of nk
                if 0
                    vectorPointersnk = updatePointers(vectorPointersnk, MAX_nk, MIN_nk, INC_nk);
                end
            end
            % Update vector of pointers of nb
            if 0
                vectorPointersnb = updatePointers(vectorPointersnb, MAX_nb, MIN_nb, INC_nb);
            end
        end
        
        opt = armaxOptions('Focus', 'stability');
        stateSystem = armax(data, orders, 'InputDelay', inputDelay,...
            'ioDelay', ioDelay,...
            'IntegrateNoise', integrateNoise, opt);
    end
    
    
    %% SAVE
    function saveModel(model, orders, data, name)
        out = strcat(outputDir, '/', name);
        checkForMedia(out, true, true);
        
        % Comparing Model Output to Measured Output
        if strcmp(METRIC, 'fit') % METRIC: fit
            [predictedOutputComp, metricT, ~] = compare(data,  model.stateSystem);
        elseif strcmp(METRIC, 'mse')
            predictedOutputComp = compare(data, model.stateSystem);
            metricT = mean((data.y - predictedOutputComp.y).^2);
        end
        model.fitness = metricT;
        model.orders = orders;
        
        if ~isempty(data.u)
            maxna = max(orders(:,1:size(data.y,2)));
            maxnb =  max(orders(:,size(data.y,2)+1: size(data.y,2)+size(data.u,2)));
            maxnc = max(orders(:,size(data.y,2)+size(data.u,2)+1: 2*size(data.y,2)+size(data.u,2)));
            maxnk = max(orders(:,2*size(data.y,2)+size(data.u,2)+1:2*size(data.y,2)+2*size(data.u,2)));
        else
            maxna = max(orders(:,1:size(data.y,2)));
            maxnc =  max(orders(:,size(data.y,2)+1:size(data.u,2)));
        end
        
        % PLOT
        fig = figure('Visible','off');
        plot([predictedOutputComp.y, data.y]);
        legend = {'modeled output','original output'};
        if ~isempty(data.u)
            saveAndPrint(fig, strcat(out, '/modelARMAX'), 'fig',...
                legend,...
                sprintf('%s\n%s: %2.2g%%, na%.0dnb%.0dnc%.0dnk%.0d',...
                name, METRIC, metricT,...
                maxna, maxnb, maxnc, maxnk));
        else
            saveAndPrint(fig, strcat(out, '/modelARMAX'), 'fig',...
                legend,...
                sprintf('%s\n%s: %2.2g%%, na%.0dnc%.0d',...
                name, METRIC, metricT,...
                maxna, maxnc));
        end
        
        % Save struct in mat file
        save(strcat(out, '/modelARMAX'), '-struct', 'model');
        
        % Save info in the temporary CSV file
        comma_str = repmat(sprintf(','), 1, MAX_NUMBER_OF_INPUTS-length(inNames));
        writeInFile(reportFile, ...
            sprintf('%s%s%s,%s,%s,%s,%s,%s\n',...
            char(sprintf(cell2mat(cellfun(@(x) [x ','], inNames, 'UniformOutput', false)))),...
            comma_str,...
            model.stateSystem.Report.OptionsUsed.Focus,...
            num2str(max(orders(:,1:size(data.y,2)))),...
            num2str(maxnb),...
            num2str(maxnc),...
            num2str(maxnk),...
            num2str(metricT)));
    end
    
    %% VALIDATE ARMAX MODEL
    function [stateSystem, initialStatesX0, predictedData] =...
            validateARMAXModel(stateSystemDir, predictorsNames, yName)        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %% OJO, ESTO ESTA SIN AUTOMATIZAR!!!
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Load migraines
        rootDirModels= '/home/josueportiz/Dropbox/parsedDataPatients/patients/patient_2/data/data_60/';
        rootDirMigs= '/home/josueportiz/Dropbox/parsedDataPatients/patients/patient_2/data/data_60/';
        mig1= 'data_201405310930-201406010530';
        mig2= 'data_201406011500-201406021100';
        mig3= 'data_201406021430-201406031030';
        mig4= 'data_201406031200-201406040800';
        
        % Paciente 1 = paciente 2 sin EDA
        % Migrañas de la 5-8 no valen (datos malos)
        mig9= 'data_201404051800-201404061400';
        mig10= 'data_201404061430-201404071030';
        
     
        % Models
        % 4 vbles: TEMP_EDA_HR_SPO2
        predictorsNames = {'TEMP' 'EDA' 'HR_Plux' 'SPO2'};
        
        model_mig1= 'model_na22nb22nc10nk10_of_TEMP_EDA_HR_Plux_SPO2_output';
        model_mig2= 'model_na4nb4nc20nk20_of_TEMP_EDA_HR_Plux_SPO2_output';
        model_mig3= 'model_na26nb26nc10nk10_of_TEMP_EDA_HR_Plux_SPO2_output';
        model_mig4= 'model_na7nb7nc5nk5_of_TEMP_EDA_HR_Plux_SPO2_output';
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/armax/na-eq-nb_nc-eq-nk_metric-mse/', mod);
            stateSystemDir = strcat(modelo,'/modelARMAX.mat');
            
            modelSelected = load(stateSystemDir);
            stateSystem = modelSelected.stateSystem;
            orders = modelSelected.orders;
            normalization = modelSelected.normalization;
            
            for d=1:4
                % Load data to test
                dataMig = eval(strcat('mig',num2str(d)));
                inputDir = strcat(rootDirMigs, dataMig);
                
                
                [predictors, ~, y, ~, ~] =...
                    loadVariables(inputDir, predictorsNames, yName, normalization);
                if size(predictors,2) ~= length(predictorsNames)
                    predictorNamesString = cell2mat(cellfun(@(x) [x ', '], predictorsNames, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'Some of these predictors: %s do not exist in the directory:\n %s',...
                        predictorNamesString, inputDir);
                elseif size(y,2) ~= length(yName)
                    outputNamesString = cell2mat(cellfun(@(x) [x ', '], yName, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'The outputs: %s do not exist in the directory:\n %s',...
                        outputNamesString, inputDir);
                end
                
                % Create a data object. Just time dimain data, ARMAX does
                % not read frequency data.
                if strcmp(stateSystem.Report.DataUsed.Type, 'Time domain data')
                    dataToValidate = iddata(y, predictors, stateSystem.Ts);
                    dataToValidate.TimeUnit = stateSystem.TimeUnit;
                else
                    error('ErrorTests:convertTest', ...
                        'Domain must be ''Time'' or ''Frequency''');
                end
                dataToValidate.una = predictorsNames;
                dataToValidate.yna = yName;
                
                
                % Crete log file
                stateSystem.Name = strcat(mod); % Usar el que tenga que ser
                reporFileName =  strcat('log_validation_', stateSystem.Name,'.csv');
                
                % Write header
                writeInFile(reporFileName, sprintf(strcat('Test data: ',inputDir,'\n')));
                writeInFile(reporFileName, sprintf('Horizon (min),Fitting\n'));
                
                if strcmp(METRIC, 'fit') % METRIC: fit
                    prevFit = 0;
                elseif strcmp(METRIC, 'mse')
                    prevFit = Inf;
                end
                % Validate:
                if strcmp(METRIC, 'fit') % METRIC: fit
                    for i = 1:200
                        [~, metricT, ~] = compare(dataToValidate, stateSystem,i);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT > prevFit
                            prevFit = metricT;
                        end
                    end
                elseif strcmp(METRIC, 'mse')
                    for i = 1:200
                        yp = compare(dataToValidate, stateSystem,i);
                        metricT = mean((dataToValidate.y - yp.y).^2);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT < prevFit
                            prevFit = metricT;
                        end
                    end
                end
            end
        end
        
        % 3 vbles: TEMP_HR_SPO2
        predictorsNames = {'TEMP' 'HR_Plux' 'SPO2'};
        model_mig1= 'model_na29nb29nc5nk5_of_TEMP_HR_Plux_SPO2_output';
        model_mig2= 'model_na27nb27nc15nk15_of_TEMP_HR_Plux_SPO2_output';
        model_mig3= 'model_na26nb26nc25nk25_of_TEMP_HR_Plux_SPO2_output';
        model_mig4= 'model_na7nb7nc30nk30_of_TEMP_HR_Plux_SPO2_output';
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/armax/na-eq-nb_nc-eq-nk_metric-mse/', mod);
            stateSystemDir = strcat(modelo,'/modelARMAX.mat');
            
            modelSelected = load(stateSystemDir);
            stateSystem = modelSelected.stateSystem;
            orders = modelSelected.orders;
            normalization = modelSelected.normalization;
            
            for d=1:4
                % Load data to test
                dataMig = eval(strcat('mig',num2str(d)));
                inputDir = strcat(rootDirMigs, dataMig);
                
                
                [predictors, ~, y, ~, ~] =...
                    loadVariables(inputDir, predictorsNames, yName, normalization);
                if size(predictors,2) ~= length(predictorsNames)
                    predictorNamesString = cell2mat(cellfun(@(x) [x ', '], predictorsNames, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'Some of these predictors: %s do not exist in the directory:\n %s',...
                        predictorNamesString, inputDir);
                elseif size(y,2) ~= length(yName)
                    outputNamesString = cell2mat(cellfun(@(x) [x ', '], yName, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'The outputs: %s do not exist in the directory:\n %s',...
                        outputNamesString, inputDir);
                end
                
                % Create a data object. Just time dimain data, ARMAX does
                % not read frequency data.
                if strcmp(stateSystem.Report.DataUsed.Type, 'Time domain data')
                    dataToValidate = iddata(y, predictors, stateSystem.Ts);
                    dataToValidate.TimeUnit = stateSystem.TimeUnit;
                else
                    error('ErrorTests:convertTest', ...
                        'Domain must be ''Time'' or ''Frequency''');
                end
                dataToValidate.una = predictorsNames;
                dataToValidate.yna = yName;
                
                
                % Crete log file
                stateSystem.Name = strcat(mod); % Usar el que tenga que ser
                reporFileName =  strcat('log_validation_', stateSystem.Name,'.csv');
                
                % Write header
                writeInFile(reporFileName, sprintf(strcat('Test data: ',inputDir,'\n')));
                writeInFile(reporFileName, sprintf('Horizon (min),Fitting\n'));
                
                if strcmp(METRIC, 'fit') % METRIC: fit
                    prevFit = 0;
                elseif strcmp(METRIC, 'mse')
                    prevFit = Inf;
                end
                % Validate:
                if strcmp(METRIC, 'fit') % METRIC: fit
                    for i = 1:200
                        [~, metricT, ~] = compare(dataToValidate, stateSystem,i);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT > prevFit
                            prevFit = metricT;
                        end
                    end
                elseif strcmp(METRIC, 'mse')
                    for i = 1:200
                        yp = compare(dataToValidate, stateSystem,i);
                        metricT = mean((dataToValidate.y - yp.y).^2);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT < prevFit
                            prevFit = metricT;
                        end
                    end
                end
            end
        end
        
        
        % 3 vbles: TEMP_EDA_HR
        predictorsNames = {'TEMP' 'EDA' 'HR_Plux'};
        model_mig1= 'model_na21nb21ncnk_of_TEMP_EDA_HR_Plux_output';
        model_mig2= 'model_na16nb16nc20nk20_of_TEMP_EDA_HR_Plux_output';
        model_mig3= 'model_na14nb14nc25nk25_of_TEMP_EDA_HR_Plux_output';
        model_mig4= 'model_na17nb17nc5nk5_of_TEMP_EDA_HR_Plux_output';
        % Migrañas 1-4. Paciente 2
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/armax/na-eq-nb_nc-eq-nk_metric-mse/', mod);
            stateSystemDir = strcat(modelo,'/modelARMAX.mat');
            
            modelSelected = load(stateSystemDir);
            stateSystem = modelSelected.stateSystem;
            orders = modelSelected.orders;
            normalization = modelSelected.normalization;
            
            for d=1:4
                % Load data to test
                dataMig = eval(strcat('mig',num2str(d)));
                inputDir = strcat(rootDirMigs, dataMig);
                
                
                [predictors, ~, y, ~, ~] =...
                    loadVariables(inputDir, predictorsNames, yName, normalization);
                if size(predictors,2) ~= length(predictorsNames)
                    predictorNamesString = cell2mat(cellfun(@(x) [x ', '], predictorsNames, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'Some of these predictors: %s do not exist in the directory:\n %s',...
                        predictorNamesString, inputDir);
                elseif size(y,2) ~= length(yName)
                    outputNamesString = cell2mat(cellfun(@(x) [x ', '], yName, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'The outputs: %s do not exist in the directory:\n %s',...
                        outputNamesString, inputDir);
                end
                
                % Create a data object. Just time dimain data, ARMAX does
                % not read frequency data.
                if strcmp(stateSystem.Report.DataUsed.Type, 'Time domain data')
                    dataToValidate = iddata(y, predictors, stateSystem.Ts);
                    dataToValidate.TimeUnit = stateSystem.TimeUnit;
                else
                    error('ErrorTests:convertTest', ...
                        'Domain must be ''Time'' or ''Frequency''');
                end
                dataToValidate.una = predictorsNames;
                dataToValidate.yna = yName;
                
                
                % Crete log file
                stateSystem.Name = strcat(mod); % Usar el que tenga que ser
                reporFileName =  strcat('log_validation_', stateSystem.Name,'.csv');
                
                % Write header
                writeInFile(reporFileName, sprintf(strcat('Test data: ',inputDir,'\n')));
                writeInFile(reporFileName, sprintf('Horizon (min),Fitting\n'));
                
                if strcmp(METRIC, 'fit') % METRIC: fit
                    prevFit = 0;
                elseif strcmp(METRIC, 'mse')
                    prevFit = Inf;
                end
                % Validate:
                if strcmp(METRIC, 'fit') % METRIC: fit
                    for i = 1:200
                        [~, metricT, ~] = compare(dataToValidate, stateSystem,i);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT > prevFit
                            prevFit = metricT;
                        end
                    end
                elseif strcmp(METRIC, 'mse')
                    for i = 1:200
                        yp = compare(dataToValidate, stateSystem,i);
                        metricT = mean((dataToValidate.y - yp.y).^2);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT < prevFit
                            prevFit = metricT;
                        end
                    end
                end
            end
        end
        % Migrañas 9-10. Paciente 1
        rootDirMigs= '/home/josueportiz/Dropbox/parsedDataPatients/patients/patient_1/data/data_60/';
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/armax/na-eq-nb_nc-eq-nk_metric-mse/', mod);
            stateSystemDir = strcat(modelo,'/modelARMAX.mat');
            
            modelSelected = load(stateSystemDir);
            stateSystem = modelSelected.stateSystem;
            orders = modelSelected.orders;
            normalization = modelSelected.normalization;
            
            for d=9:10
                % Load data to test
                dataMig = eval(strcat('mig',num2str(d)));
                inputDir = strcat(rootDirMigs, dataMig);
                
                
                [predictors, ~, y, ~, ~] =...
                    loadVariables(inputDir, predictorsNames, yName, normalization);
                if size(predictors,2) ~= length(predictorsNames)
                    predictorNamesString = cell2mat(cellfun(@(x) [x ', '], predictorsNames, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'Some of these predictors: %s do not exist in the directory:\n %s',...
                        predictorNamesString, inputDir);
                elseif size(y,2) ~= length(yName)
                    outputNamesString = cell2mat(cellfun(@(x) [x ', '], yName, 'UniformOutput', false));
                    error('ErrorTests:convertTest', ...
                        'The outputs: %s do not exist in the directory:\n %s',...
                        outputNamesString, inputDir);
                end
                
                % Create a data object. Just time dimain data, ARMAX does
                % not read frequency data.
                if strcmp(stateSystem.Report.DataUsed.Type, 'Time domain data')
                    dataToValidate = iddata(y, predictors, stateSystem.Ts);
                    dataToValidate.TimeUnit = stateSystem.TimeUnit;
                else
                    error('ErrorTests:convertTest', ...
                        'Domain must be ''Time'' or ''Frequency''');
                end
                dataToValidate.una = predictorsNames;
                dataToValidate.yna = yName;
                
                
                % Crete log file
                stateSystem.Name = strcat(mod); % Usar el que tenga que ser
                reporFileName =  strcat('log_validation_', stateSystem.Name,'.csv');
                
                % Write header
                writeInFile(reporFileName, sprintf(strcat('Test data: ',inputDir,'\n')));
                writeInFile(reporFileName, sprintf('Horizon (min),Fitting\n'));
                
                if strcmp(METRIC, 'fit') % METRIC: fit
                    prevFit = 0;
                elseif strcmp(METRIC, 'mse')
                    prevFit = Inf;
                end
                % Validate:
                if strcmp(METRIC, 'fit') % METRIC: fit
                    for i = 1:200
                        [~, metricT, ~] = compare(dataToValidate, stateSystem,i);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT > prevFit
                            prevFit = metricT;
                        end
                    end
                elseif strcmp(METRIC, 'mse')
                    for i = 1:200
                        yp = compare(dataToValidate, stateSystem,i);
                        metricT = mean((dataToValidate.y - yp.y).^2);
                        writeInFile(reporFileName , ...
                            sprintf('%s,%s\n',...
                            num2str(i), num2str(metricT)));
                        
                        if metricT < prevFit
                            prevFit = metricT;
                        end
                    end
                end
            end
        end
    end
    
    %% LOCAL FUNCTIONS
    function [indexes] = updatePointers(indexes, maxi, mini, inc)
        % Update output's index
        if (min(indexes) == maxi) % Count restarted
            carry = 0;
        else
            carry = 1;
        end
        
        % Update indexes vector
        while carry ~= 0
            carry = 0;
            for i=1:size(indexes,1)
                for j=1:size(indexes,2)
                    if (indexes(i,j) < maxi)
                        indexes(i,j) = indexes(i,j) + inc;
                        carry = 0;
                        break;
                    else
                        indexes(i,j) = mini;
                        carry = 1;
                    end
                end
            end
        end
    end
    
    
    
    
    function saveAndPrint(varargin)
        fig = varargin{1};
        dir = varargin{2};
        opt = varargin{3};
        
        switch nargin
            case 4
                if ischar(varargin{4})
                    texto = varargin{4};
                    suptitle(texto);
                elseif iscell(varargin{4})
                    legend(varargin{4})
                end
            case 5
                texto = cellfun(@(x) [x '_'], varargin(5), 'UniformOutput', false);
                suptitle(texto);
                legend(varargin{4});
            otherwise
                error('ErrorTests:convertTest', ...
                    'Bad number of inputs');
        end
        
        
        % Store as PDF and EPS
        orient landscape
        print(fig, '-dpdf', dir)
        print(fig, '-deps', dir)
        
        % Save figure
        saveas(fig, dir, opt)
    end
    
    function writeInFile(fileName, textToWrite)
        % Write into a file. Usually a log file
        fileID = fopen(fileName, 'a');
        fprintf(fileID, textToWrite);
        fclose (fileID );
    end
end % Main
