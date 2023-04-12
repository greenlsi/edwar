function runARX(varargin)
     dbstop at 7
%     dbstop at 172
%     dbstop at 442
    
    %% CONSTANTS
    df_MNOI = str2double(getenv('df_MAX_NUMBER_OF_INPUTS'));
    target = getenv('dftarget');

    %% PARSE INPUTS
    mode = varargin{1};
    inputDir = varargin{2};
    outputDir = varargin{3};
    
    %% CREATE OR VALIDATE MODEL
    switch mode
        case 'create' % Create a new model from data
            reportFile = strcat('log_Models', upper('arx'),'.txt');
            
            nx = varargin{4}; % The model's orders
            opts = varargin{5};
            norm = varargin{6}; % Normalize data or not (TRUE or FALSE)
            dataInfo = varargin{7}; % 4 elements vector: Time, NOT frequency, Units, storageRate, fs
            inNames = varargin{8};
            outName = varargin{9}; % To compare with
            
            % Create the model
            [model, dataRead, orders] = ...
                createarxModel(nx, opts, norm, dataInfo, inNames, outName); % Call function
            if ~isempty(inNames)
              fileName = char(strcat('model_',...
                    sprintf('na%.0dnb%.0dnk%.0d',max(orders(:,1:size(dataRead.y,2))),...
                    max(orders(:,size(dataRead.y,2)+1:size(dataRead.u,2))),...
                    max(orders(:,size(dataRead.y,2)+size(dataRead.u,2)+1: 2*size(dataRead.y,2)+size(dataRead.u,2)))),...
                    '_of_',...
                    cell2mat(cellfun(@(x) [x '_'], inNames, 'UniformOutput', false)), outName));
            else
               fileName = char(strcat('model_',...
                    sprintf('na%.0d',max(orders(:,1:size(dataRead.y,2))),...
                    max(orders(:,size(dataRead.y,2)+1:size(dataRead.u,2)))),...                    
                    '_of_',...
                    cell2mat(cellfun(@(x) [x '_'], inNames, 'UniformOutput', false)), outName));
            end
            
          
            % Save and print the results.
            % Compare model with the original output
            modelStruct = struct('stateSystem', model,...
                'fitness',0,...
                'orders',[],...
                'normalization', norm);
            savearxModel(modelStruct, orders, dataRead, fileName);
        case 'validate' % Validate an existing model for data
            reportFile = strcat('log_Validation_Models', upper('arx'),'.txt');
            
            modelDir = varargin{4};
            inNames = varargin{5};
            outName = varargin{6}; % To compare with
            
            % Validate the model
            [model, ~, predictedData] =...
                validatearxModel(modelDir, inNames, outName);
%             fileName = char(strcat('prediction_',...
%                 sprintf('P%.0dF%.0d',model.Report.N4Horizon(3), model.Report.N4Horizon(1)),...
%                 '_of_',...
%                 cell2mat(cellfun(@(x) [x '_'], inNames, 'UniformOutput', false)), outName));
%             
%             % Save and print the results.
%             % Compare model with the original output
%             savearxModel(model, predictedData, fileName);
    end

    
    %% CREATE arx MODEL
    function [stateSystem, data, orders] =...
            createarxModel(ordersModel, algorithmOptions, normalization, domainInfo, predictorsNames, yName)
        %% Variables
        % Options for model
        opt = arxOptions; % Default values
        
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
        
         %% TOUSE
%         for i=1:2:length(algorithmOptions)
%             name = algorithmOptions{i};
%             value = algorithmOptions{i+1};
%             switch name
%                 case 'InitialCondition'
%                     % Default: 'auto'
%                     opt.InitialState = value;
%                 case 'Focus'
%                     % Default: 'prediction'
%                     opt.Focus = value;
%                 case 'EstCovar'
%                     % Default: 'true'
%                     opt.EstCovar = value;
%                 case 'Display'
%                     % Default: 'off'
%                     opt.Display = value;
%                 case 'InputOffset'
%                     % Default: []
%                     opt.InputOffset = value;
%                 case 'OutputOffset'
%                     % Default: []
%                     opt.OutputOffset = value;
%                 case 'SearchMethod'
%                     % Default: 'auto'
%                     opt.SearchMethod = value;
%                 case 'SearchOption'
%                     % Default: Depends on the search method
%                     opt.SearchMethod = value;
%                 case 'Advanced' %% TODO
%                     % Default: structure{..}
%                     opt.Advanced = value;
%                     %% Specify optional comma-separated pairs of Name,Value arguments
%                 case 'InputDelay'
%                     % Default: 0
%                     inputDelay= value;
%                 case 'ioDelay'
%                     % Default: 0 for all input/output pair
%                     ioDelay = value;
%                 case 'IntegrateNoise'
%                     % Default: false(Ny,1) (Ny is the number of outputs)
%                     integrateNoise = value;
%                 otherwise
%                     error('ErrorTests: convertTest', ...
%                         'The option: %s do not exist for arx', name);
%             end
%         end
%         
%         if (~min(isscalar(ordersModel)) && ...
%                 ~strcmp(ordersModel, 'best'))
%             error('ErrorTests:convertTest', ...
%                 'Order of stimated model must be a scalar or vector, or ''best''');
%         else
%             if length(ordersModel) == 4 % arx or arx if 'IntegrateNoise' option is true.
%                 na = ordersModel{1};
%                 nb = ordersModel{2};
%                 nc = ordersModel{3};
%                 nk = ordersModel{4};
%                 arxOrders = [na nb nc nk];
%             elseif length(ordersModel) == 2 % ARMA or ARIMA if 'IntegrateNoise' option is true.
%                 na = ordersModel{1};
%                 nc = ordersModel{2};
%                 arxOrders = [na nc];
%             end
%         end
%         %%
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
        
        %% APPLY arx ALGORITHM
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
        
        MIN_nk = 0;
        INC_nk = 5;        
        if ~isempty(predictorsNames)
            MAX_nk = 40;            
        else
            MAX_nk = 0;
        end
        
        
        
        
        % If selected order is too big reduce it
        prevFit = 0;
        inputDelay = 0;
        ioDelay = 0;
        % ARX
        integrateNoise = false; 
        vuelta = 1;
        % Init
        vectorPointersnb = zeros(length(yName), length(predictorsNames));
        vectorPointersnk = zeros(length(yName), length(predictorsNames));
                
        for na = MAX_na:-1:MIN_na
            switch target
                case 'migraine'
                    % Just one output, Ny = 1
                    na_ = na; % Ny-by-Ny matrix.
                otherwise
                    error('ErrorTests:convertTest', ...
                        'Bad target selected');
            end
            %for nb = MAX_nb:-1:MIN_nb
                % In this first aproximation use the same order for each
                % variable
                %nb_ = repmat(nb, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
                %nb_ = vectorPointersnb;
                nb_ = repmat(na, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
            
                for nk = MAX_nk:-INC_nk:MIN_nk % input-output delay
                    %while min(vectorPointersnk) < MAX_nk
                    % In this first aproximation use the same order for each
                    % variable
                    %nk_ = repmat(nk, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
                    %nk_= vectorPointersnk;
                    nk_ = repmat(nk, length(yName), length(predictorsNames)); % Ny-by-Nu matrix
                    
                    try
                        % TODO
                        fprintf('Vuelta:%d\nna:%d\nnb:%d\nnk:%d\n\n', vuelta, na_, nb_(1), nk_(1))
                        opt = arxOptions('Focus', 'stability');
                        stateSystem = arx(data, [na_ nb_ nk_],...
                            'InputDelay', inputDelay,...
                            'ioDelay', ioDelay,...
                            'IntegrateNoise', integrateNoise, opt);
                        vuelta = vuelta + 1;
                        
                        [~, fit, ~]= compare(data, stateSystem);
                        if fit > prevFit
                            prevFit = fit;
                            orders = [na_ nb_ nk_];
                        end
                    catch E
                    end
                    % Update vector of pointers of nk
                %vectorPointersnk = updatePointers(vectorPointersnk, MAX_nk, MIN_nk, INC_nk);
                end
                
                % Update vector of pointers of nb
                %vectorPointersnb = updatePointers(vectorPointersnb, MAX_nb, MIN_nb, INC_nb);
            %end
        end
        
        opt = arxOptions('Focus', 'stability');
        stateSystem = arx(data, orders, 'InputDelay', inputDelay,...
                                'ioDelay', ioDelay,...
                                'IntegrateNoise', integrateNoise, opt);
    end
    
    
    %% SAVE
    function savearxModel(model, orders, data, name)
        out = strcat(outputDir, '/', name);
        checkForMedia(out, true, true);
        
        % Comparing Model Output to Measured Output
        [predictedOutputComp, fit, ~] = compare(data, model.stateSystem);
        model.fitness = fit;
        model.orders = orders;
        
        if ~isempty(data.u)
            maxna = max(orders(:,1:size(data.y,2)));
            maxnb =  max(orders(:,size(data.y,2)+1: size(data.y,2)+size(data.u,2)));
            maxnk = max(orders(:,size(data.y,2)+size(data.u,2)+1: 2*size(data.y,2)+size(data.u,2)));            
        else
            maxna = max(orders(:,1:size(data.y,2)));            
        end
        
        % PLOT
        fig = figure('Visible','off');
        plot([predictedOutputComp.y, data.y]);
        legend = {'modeled output','original output'};
        if ~isempty(data.u)
            saveAndPrint(fig, strcat(out, '/modelarx'), 'fig',...
                legend,...
                sprintf('%s\nFit: %2.2g%%, na%.0dnb%.0dnk%.0d',...
                name, fit,...
                maxna, maxnb, maxnk));
        else
            saveAndPrint(fig, strcat(out, '/modelarx'), 'fig',...
                legend,...
                sprintf('%s\nFit: %2.2g%%, na%.0d',...
                name, fit,...
                maxna));
        end
        
        % Save struct in mat file
        save(strcat(out, '/modelarx'), '-struct', 'model');
        
        % Save info in the temporary CSV file
        comma_str = repmat(sprintf(','), 1, df_MNOI-length(inNames));
        writeInFile(reportFile, ...
            sprintf('%s%s%s,%s,%s,%s,%s,%s\n',...
            char(sprintf(cell2mat(cellfun(@(x) [x ','], inNames, 'UniformOutput', false)))),...
            comma_str,...
            model.stateSystem.Report.OptionsUsed.Focus,...
            num2str(max(orders(:,1:size(data.y,2)))),...
            num2str(maxnb),...
            num2str(maxnk),...
            num2str(fit)));
    end
    
    %% VALIDATE arx MODEL
    function [stateSystem, initialStatesX0, predictedData] =...
            validatearxModel(stateSystemDir, predictorsNames, yName)
        
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
        
        
% Variables
% predictorsNames = {'TEMP', 'EDA', 'HR_Plux', 'SPO2'};


        % Models
        % 4 vbles: TEMP_EDA_HR_SPO2
         model_mig1= 'model_na21nb21nk_of_TEMP_EDA_HR_Plux_SPO2_output'
         model_mig2= 'model_na27nb27nk5_of_TEMP_EDA_HR_Plux_SPO2_output';
         model_mig3= 'model_na30nb30nk25_of_TEMP_EDA_HR_Plux_SPO2_output';
         model_mig4= 'model_na30nb30nk25_of_TEMP_EDA_HR_Plux_SPO2_output';
         for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/arx/na-eq-nb_nc-eq-nk/', mod);
            stateSystemDir = strcat(modelo,'/modelarx.mat');
            
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
                
                % Create a data object. Just time dimain data, arx does
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
                writeInFile(reporFileName, sprintf(strcat('Model: ',stateSystemDir,'\n')));
                writeInFile(reporFileName, sprintf(strcat('Migraine: ',stateSystemDir,'\n')));
                writeInFile(reporFileName, sprintf(strcat('Test data: ',inputDir,'\n')));
                writeInFile(reporFileName, sprintf('Horizon (min),Fitting\n'));
                
                prevFit = 0;
                for i = 1:200
                    [~, fit, ~] = compare(dataToValidate, stateSystem,i);
                    writeInFile(reporFileName , ...
                        sprintf('%s,%s\n',...
                        num2str(i), num2str(fit)));
                    
                    if fit > prevFit
                        prevFit = fit;
                        bestHorizon = i; % the best horizon
                    end
                end
            end
       end
        
       
        % 3 vbles: TEMP_HR_SPO2
predictorsNames = {'TEMP', 'HR_Plux', 'SPO2'};
         model_mig1= 'model_na30nb30nk10_of_TEMP_HR_Plux_SPO2_output'
         model_mig2= 'model_na28nb28nk25_of_TEMP_HR_Plux_SPO2_output';
         model_mig3= 'model_na17nb17nk40_of_TEMP_HR_Plux_SPO2_output';
         model_mig4= 'model_na2nb2nk35_of_TEMP_HR_Plux_SPO2_output';
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/arx/na-eq-nb_nc-eq-nk/', mod);
            stateSystemDir = strcat(modelo,'/modelarx.mat');
            
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
                
                % Create a data object. Just time dimain data, arx does
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
                
                prevFit = 0;
                for i = 1:200
                    [~, fit, ~] = compare(dataToValidate, stateSystem,i);
                    writeInFile(reporFileName , ...
                        sprintf('%s,%s\n',...
                        num2str(i), num2str(fit)));
                    
                    if fit > prevFit
                        prevFit = fit;
                        bestHorizon = i; % the best horizon
                    end
                end
            end
        end
        
        
        
         % 3 vbles: TEMP_EDA_HR
         predictorsNames = {'TEMP', 'EDA', 'HR_Plux'};
         model_mig1= 'model_na21nb21nk_of_TEMP_EDA_HR_Plux_output';
         model_mig2= 'model_na28nb28nk5_of_TEMP_EDA_HR_Plux_output';
         model_mig3= 'model_na25nb25nk_of_TEMP_EDA_HR_Plux_output';
         model_mig4= 'model_na30nb30nk_of_TEMP_EDA_HR_Plux_output';
         % Migrañas 1-4
         for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/arx/na-eq-nb_nc-eq-nk/', mod);
            stateSystemDir = strcat(modelo,'/modelarx.mat');
            
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
                
                % Create a data object. Just time dimain data, arx does
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
                
                prevFit = 0;
                for i = 1:200
                    [~, fit, ~] = compare(dataToValidate, stateSystem,i);
                    writeInFile(reporFileName , ...
                        sprintf('%s,%s\n',...
                        num2str(i), num2str(fit)));
                    
                    if fit > prevFit
                        prevFit = fit;
                        bestHorizon = i; % the best horizon
                    end
                end
            end
        end        
        % Migrañas 9-10
        rootDirMigs= '/home/josueportiz/Dropbox/parsedDataPatients/patients/patient_1/data/data_60/';
        for m=1:4
            % Load model
            modelMig = eval(strcat('mig',num2str(m)));
            mod = eval(strcat('model_mig',num2str(m)));
            
            modelo = strcat(rootDirModels, modelMig, '/algorithms/arx/na-eq-nb_nc-eq-nk/', mod);
            stateSystemDir = strcat(modelo,'/modelarx.mat');
            
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
                
                % Create a data object. Just time dimain data, arx does
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
                
                prevFit = 0;
                for i = 1:200
                    [~, fit, ~] = compare(dataToValidate, stateSystem,i);
                    writeInFile(reporFileName , ...
                        sprintf('%s,%s\n',...
                        num2str(i), num2str(fit)));
                    
                    if fit > prevFit
                        prevFit = fit;
                        bestHorizon = i; % the best horizon
                    end
                end
            end
        end
        
        %% TOUSE
        %%%%%%%%%%%%%
%         % Predicted Output
%         % Get the output predicted
%         fs = predictOptions( 'InitialCondition', initialStatesX0)
%         predictedData = predict(stateSystem, dataToValidate, 100,fs)
%         
%         % Compare
%         [~, fit, ~]=    compare(dataToValidate, stateSystem)
%         
%         
%         % Simulate
%         optSim = simOptions( 'InitialCondition', initialStatesX0)
%         predictedData = sim(stateSystem, dataToValidate, optSim)
%         % Simulated OUTPUT
%         % Make simulation from the model and the predictors.
%         % predictedOutputSim = sim(stateSystem,data.InputData, simOptions('AddNoise',true));
%                 
        
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
