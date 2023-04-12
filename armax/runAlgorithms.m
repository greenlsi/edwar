function runAlgorithms(varargin)
% This code made (2^inputVars)-1 calls to the correspondent algorithm.
% All these combinations are made for normalization and no normalization of
% variables.
% Total= 2*((2^inputVars)-1) outputs

% Usage:
%dbstop at 11; %dbstop at 233
%% PARSE INPUTS
DEFAULT_NARGIN = 3;
df_dataName=getenv('df_dataName');


algorithmName = varargin{1};
mode = varargin{2};

switch algorithmName
    case {'ge','n4sid', 'arx', 'armax', 'arimax'}
        metric = varargin{3};
        switch mode
            case 'create'
                uniqueHorizon = varargin{4};
                narginOffset = 1;
            case {'validation', 'test'}
                predictionTime = varargin{4};
                uniqueHorizon = varargin{5};
                cv = varargin{6}; % Cross-validation
                mRepair = varargin{7}; % Model repair yes or not
                fitG = varargin{8};
                detection = varargin{9}; % Plot average sympthomatic prediction
                saturateVar = varargin{10};
                varToSat = varargin{11};
                valueSat = varargin{12};
                averageModels = varargin{13};
                
                narginOffset = 10;
            otherwise
                error('ErrorTests:convertTest', ...
                    'Not defined mode: %s for algortihm: %s\n',...
                    mode, algorithmName)
        end
        % Normalization and options added to the algorithm options file
        optionsAdded = 2; % DOMAIN DATA AND MODEL ORDER IN THIS CASE
    case {'zoh'}
        metric = varargin{3};
        switch mode
            case {'validation'}
                predictionTime = varargin{4};
                narginOffset = 1;
            otherwise
                error('ErrorTests:convertTest', ...
                    'Not defined mode: %s for algortihm: %s\n',...
                    mode, algorithmName)
        end
        % Normalization and options added to the algorithm options file
        optionsAdded = 0; % DOMAIN DATA AND MODEL ORDER IN THIS CASE
    case {'kalman'}
        metric = varargin{3};
        switch mode
            case 'create'
                narginOffset = 1;
            case  {'validation', 'test'}
                pathToModel = varargin{6};
                predictionTime = varargin{7};
                narginOffset = 3;
            otherwise
                error('ErrorTests:convertTest', ...
                    'Not defined mode: %s for algortihm: %s\n',...
                    mode, algorithmName)
        end
        % Normalization and options added to the algorithm options file
        optionsAdded = 0; % DOMAIN DATA AND MODEL ORDER IN THIS CASE
    case 'lasso'
        narginOffset = 0;
        optionsAdded = 0;
    otherwise
        error('ErrorTests:convertTest', ...
            'Not defined code for algortihm: %s\n',...
            algorithmName)
end

inputDir = varargin{DEFAULT_NARGIN + narginOffset + 1};

%   Validation and test do not receive variables
if strcmp(mode, 'create')
    inputVars = varargin{DEFAULT_NARGIN + narginOffset + 2};
    outputVar = varargin{DEFAULT_NARGIN + narginOffset + 3};
else
    inputVars = [];
    outputVar = [];
end

switch nargin
    case DEFAULT_NARGIN + narginOffset + 4
        windowSizeSec = varargin{nargin};
        normalization = false;
    case DEFAULT_NARGIN + narginOffset+ 5
        windowSizeSec = varargin{nargin-1};
        normalization = varargin{nargin};
    otherwise
        windowSizeSec = 0;
        normalization = false;
end



%% CONSTANTS
LENGTH_OF_TIMESTAMP = 12;
ORDER_MODEL_OFFSET = 1;
DOMAIN_DATA_OFFSET = 2;

df_MNOI = str2double(getenv('df_MAX_NUMBER_OF_INPUTS'));

% Add algorithms' paths and others
addpath(strcat(getenv('CODE_HOME'),'/algorithms'))

% Files
OPTIONS_FILE = strcat('/tmp','/options',upper(algorithmName),'.csv');


%% INIT VARIABLES
if ~strcmp(algorithmName, 'kalman') && ~strcmp(algorithmName, 'zoh') 
    algorithmOptions = checkForMedia(OPTIONS_FILE , '%s%s', ',', false);
    % Copy algotithms' options themselves. Later add test options, or other options.
    copyfile(OPTIONS_FILE, strcat('/tmp','/temporary','Options', upper(algorithmName),'.csv'));
    optionsFileId = fopen(strcat('/tmp','/temporary', 'Options', upper(algorithmName),'.csv'), 'a+');
    % Options, Format file:
    % 2 cols. First column with the options name; the second one with the value
    no = length(algorithmOptions{1})-optionsAdded; % Num of options
    optionsNames = algorithmOptions{:,1}(1:no);
    optionsValues = algorithmOptions{:,2}(1:no);
else
    no = 0;
    algorithmOptions = [];
end
if ~strcmp(algorithmName, 'ge') && ~strcmp(algorithmName, 'zoh') 
    outputDirRoot = checkForMedia(strcat(inputDir,'algorithms/',algorithmName), true, 1);
else
    outputDirRoot  = '';
end

%% ALGORITHM
% For all the inputs combinations
if ~isempty(inputVars)
    p = length(inputVars);
    totalVariablesCombinations = (2^p)-1;
    selectVariableMask = de2bi(0, p); % With this selectVariableMask select which variables are selected in each case
end

switch algorithmName
    case 'lasso'
        reportFile = strcat('log_', upper(algorithmName),'.txt');
        % Calculate with permutations without repetiton the number of posibilities
        % Also:
        %    for (i=1:p)
        %        totalVariablesCombinations = totalVariablesCombinations + nchoosek(p,i);
        %    end
        
        %             if (windowing)
        %                 outputDir = checkForMedia(strcat(outputDir, '/windowed'), true, 1);
        %             else
        %                 outputDir = checkForMedia(strcat(outputDir, '/no_windowed'), true, 1);
        %             end
        totalOptionsCombinations = (2^no); % Even no options
        if no
            selectOptionMask = de2bi(0, no);
        end
        
        % For all inputVars combinations
        for i=0:totalVariablesCombinations-1
            currentVars = cell(inputVars(~de2bi(bi2de(selectVariableMask)+i,p)));
            currentVarsNamesString = cell2mat(cellfun(@(x) [x ', '], currentVars, 'UniformOutput', false));
            name = char(strcat(upper(algorithmName),'_of_',...
                cell2mat(cellfun(@(x) [x '_'], currentVars, 'UniformOutput', false)),outputVar,'.mat'));
            
            for j=1:totalOptionsCombinations
                if ~no
                    opt = strcat('','');
                    % outputDir = checkForMedia(strcat(outputDirRoot, '/no_opts/'), true, 1);
                else
                    currentOptNames = cell(optionsNames(~de2bi(bi2de(selectOptionMask)+j-1,no)));
                    currentOptValues = cell(optionsValues(~de2bi(bi2de(selectOptionMask)+j-1,no)));
                    opt = parseOptions(algorithmName, currentOptNames, currentOptValues);
                    %                         optNameDirs = strcat(currentOptNames,'/');
                    %                         optNameDirs = strcat(optNameDirs{:});
                    %                         outputDir = checkForMedia(strcat(outputDirRoot, '/', optNameDirs), true, 1);
                end
                
                if ~exist(strcat(outputDir,name), 'file') % If exists do nothing
                    writeInFile('log.txt', ...
                        sprintf('%s Starting %s with opts: %s, normalization: %d\n\tfor variables: %s\n',...
                        datestr(now), algorithmName,cell2mat(cellfun(@(x) [x ', '], opt, 'UniformOutput', false)),...
                        normalization, currentVarsNamesString));
                    
                    runLasso(opt, inputDir, outputDirRoot, currentVars,...
                        outputVar, normalization, windowSizeSec);
                else
                    writeInFile('log.txt', ...
                        sprintf('%s Output for %s already exists.\n',...
                        datestr(now), name));
                end
            end
        end
    case 'ge'
        % Check if model exists
        if exist(inputDir, 'file') == 2
            runGE(mode, inputDir, outputDirRoot, metric,...
                predictionTime, uniqueHorizon, cv, detection,mRepair,fitG,...
                saturateVar, varToSat, valueSat, averageModels);
        else
            writeInFile('log.txt', ...
                sprintf('%s Model: %s does not exist\n',...
                datestr(now), inputDir));
        end
        
    case 'zoh'
        % Check if model exists
        if exist(inputDir, 'file') == 2
            runZOH(inputDir, metric, predictionTime);
        else
            writeInFile('log.txt', ...
                sprintf('%s Model: %s does not exist\n',...
                datestr(now), inputDir));
        end
    case 'n4sid'
        switch mode
            case 'create'
                % Report file
                reportFile = strcat('log_Models', upper('n4sid'),'_','.txt');
                comma_str=repmat(sprintf(','),1,df_MNOI);
                
                writeInFile(reportFile, ...
                    sprintf('\n%s\n%s\nmodel:%s\nInputs%sFocus,Past,Future,Metric,Order\n',...
                    datestr(now),...
                    df_dataName,...
                    'n4sid', comma_str));
                
                % Last 2 rows are: order for N4SID and domain data option
                orderModel = algorithmOptions{:,2}(no+ORDER_MODEL_OFFSET);
                if iscellstr(orderModel)
                    orderModel = char(orderModel);
                else
                    orderModel = cell2mat(orderModel);
                end
                domainData = regexp(algorithmOptions{:,2}{no+DOMAIN_DATA_OFFSET},';','split');
                
                % For all inputVars combinations
                for i=0:totalVariablesCombinations-1
                    currentVars = cell(inputVars(~de2bi(bi2de(selectVariableMask)+i,p)));
                    optionsStrc = parseOptions(algorithmName, optionsNames, optionsValues);
                    
                    if length(currentVars) > 2
                        % Run the algotihm
                        runN4SID('create',inputDir, outputDirRoot, metric, orderModel,...
                            uniqueHorizon, optionsStrc, normalization, domainData,...
                            currentVars, outputVar);
                    end
                end
            case {'validation', 'test'}
                % Check if model exists
                inputDataPath = str2double(regexpi(inputDir,...
                    strcat('[0-9]', '{',num2str(LENGTH_OF_TIMESTAMP),'}'),'match'));
                
                writeInFile('log.txt', ...
                    sprintf('%s Starting validation for model: %s\nand data from: %s\n',...
                    datestr(now), pathToModel, inputDataPath));
                
                if exist(pathToModel, 'dir')
                    model = strcat(pathToModel, '/modelN4SID.mat');
                    runN4SID(mode, inputDir, outputDirRoot, metric,...
                        model, predictionTime, uniqueHorizon, cv, detection,mRepair,fitG,...
                        saturateVar, varToSat, valueSat, averageModels);
                elseif exist(pathToModel, 'file') == 2
                    runN4SID(mode, inputDir, outputDirRoot, metric,...
                        pathToModel, predictionTime, uniqueHorizon, cv, detection,mRepair,fitG,...
                        saturateVar, varToSat, valueSat, averageModels);
                else
                    writeInFile('log.txt', ...
                        sprintf('%s Model: %s does not exist\n',...
                        datestr(now), pathToModel));
                end
                
        end
    case 'kalman'
        if strcmp(mode, 'create')
            %% TODO
            reportFile = strcat('log_Models', upper(algorithmName),'.txt');
            
            %             comma_str=repmat(sprintf(','),1,df_MNOI-1);
            %             writeInFile(reportFile, ...
            %                 sprintf('\n%s\ndata_%s\nmodel:%s\nInputs%sFocus,Past,Future,Fit,Order\n',...
            %                 datestr(now),...
            %                 char(regexpi(inputDir,...
            %                     strcat('[0-9]', '{',num2str(LENGTH_OF_TIMESTAMP),'}'),'match')),...
            %                 algorithmName, comma_str));
            
            % Last 2 rows are: order for N4SID and domain data option
            %             orderModel = algorithmOptions{:,2}(no+ORDER_MODEL_OFFSET);
            %             if iscellstr(orderModel)
            %                 orderModel = char(orderModel);
            %             else
            %                 orderModel = cell2mat(orderModel);
            %             end
            %domainData = regexp(algorithmOptions{:,2}{no+DOMAIN_DATA_OFFSET},';','split');
            switch mode
                case 'create'
                    %% TODO
                    % For all inputVars combinations
                    for i=0:totalVariablesCombinations-1
                        % Run the algotihm
                        runKALMAN('create',inputDir, outputDirRoot);
                    end
                case 'validation'
                    % For all inputVars combinations
                    %% TODO
                    for i=0:totalVariablesCombinations-1
                        % Check if model exists
                        currentVars = cell(inputVars(~de2bi(bi2de(selectVariableMask)+i,p)));
                        inputDataPath = str2double(regexpi(inputDir,...
                            strcat('[0-9]', '{',num2str(LENGTH_OF_TIMESTAMP),'}'),'match'));
                        
                        if exist(pathToModel, 'dir')
                            writeInFile('log.txt', ...
                                sprintf('%s Starting validation for model: %s\nand data from: %s\n',...
                                datestr(now), pathToModel, inputDataPath));
                            
                            model = strcat(pathToModel, '/modelKALMAN.mat');
                            runKALMAN('validation', inputDir, outputDirRoot,...
                                model, currentVars, outputVar);
                        else
                            writeInFile('log.txt', ...
                                sprintf('%s Model: %s does not exist\n',...
                                datestr(now), pathToModel));
                        end
                    end
            end
        elseif strcmp(mode, 'validation')
            reportFile = strcat('log_Validation_Models', upper(algorithmName),'.txt');
            % Last 2 rows are: order for N4SID and domain data option
            no = 0;
        end
        
    case {'arx', 'armax', 'arimax'}
        %% TODO
        if strcmp(mode, 'create')
            ordersModel = algorithmOptions{:,2}(no+ORDER_MODEL_OFFSET);
            if iscellstr(ordersModel)
                ordersModel = char(ordersModel);
            else
                ordersModel = cell2mat(ordersModel);
            end
            domainData = regexp(algorithmOptions{:,2}{no+DOMAIN_DATA_OFFSET},';','split');
        elseif strcmp(mode, 'validation')
            no = 0;
        end
        
        switch mode
            case 'create'
                % For all inputVars combinations
                for i=0:totalVariablesCombinations-1
                    currentVars = cell(inputVars(~de2bi(bi2de(selectVariableMask)+i,p)));
                    opt = parseOptions(algorithmName, optionsNames, optionsValues);
                    
                    % Run the algotihm
                    switch algorithmName
                        case 'arx'
                            runARX('create',inputDir, outputDirRoot, ordersModel,...
                                opt, normalization, domainData,...
                                currentVars, outputVar);
                        case {'armax', 'arimax'}
                            runARMAX('create',inputDir, outputDirRoot, algorithmName, ordersModel,...
                                opt, normalization, domainData,...
                                currentVars, outputVar);
                    end
                end
            case 'validation'
                %% CORREGIR
                % For all inputVars combinations
                for i=0:totalVariablesCombinations-1
                    % Check if model exists
                    currentVars = cell(inputVars(~de2bi(bi2de(selectVariableMask)+i,p)));
                    inputDataPath = str2double(regexpi(inputDir,...
                        strcat('[0-9]', '{',num2str(LENGTH_OF_TIMESTAMP),'}'),'match'));
                    
                    if exist(pathToModel, 'dir')
                        writeInFile('log.txt', ...
                            sprintf('%s Starting validation for model: %s\nand data from: %s\n',...
                            datestr(now), pathToModel, inputDataPath));
                        
                        switch algorithmName
                            case 'arx'
                                model = strcat(pathToModel, '/modelARX.mat');
                                runARX('validation', inputDir, outputDirRoot,...
                                    model, currentVars, outputVar);
                            case {'armax', 'arimax'}
                                model = strcat(pathToModel, '/model',upper(algorithmName),'.mat');
                                runARMAX('validation', inputDir, outputDirRoot, algorithmName,...
                                    model, currentVars, outputVar);
                        end
                    else
                        writeInFile('log.txt', ...
                            sprintf('%s Model: %s does not exist\n',...
                            datestr(now), pathToModel));
                    end
                end
        end
end
if ~strcmp(algorithmName, 'kalman') && ~strcmp(algorithmName, 'zoh') 
    fclose(optionsFileId);
end

%% LOCAL FUNTIONS
    function [opt] = parseOptions(algorithm, optNames, optValues)
        switch algorithm
            case 'lasso'
                for k=1:2:length(opt)
                    switch (char(optNames(floor(k/2)+1)))
                        case 'CV'
                            if isnumeric(str2double(optValues{k}))
                                opt{k} = optNames{floor(k/2)+1};
                                opt{k+1} = str2double(optValues{floor(k/2)+1});
                            else
                                % error aqui
                            end
                            %% TODO: all options available
                    end
                end
            case 'n4sid'
                opt = n4sidOptions;
                if ~isempty(optNames)
                    for k=1:length(2*length(optNames))
                        name = char(optNames(floor(k/2)+1));
                        switch (name)
                            case 'InitialState'
                                % Default: 'estimate'
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, 'zero') || strcmp(value, 'estimate'))
                                    opt.InitialState = value;
                                else
                                    % error aqui
                                end
                            case 'N4Weight'
                                % Default: 'auto'
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, 'MOESP') || strcmp(value, 'CVA') ||...
                                        strcmp(value, 'auto'))
                                    opt.N4Weight = value;
                                else
                                    % error aqui
                                end
                            case 'N4Horizon'
                                % Default: 'auto'
                                value = optValues{floor(k/2)+1};
                                if strcmp(value, 'auto')
                                    opt.N4Horizon = value;
                                elseif ~isempty(str2num(value)')
                                    opt.N4Horizon = str2num(value)';
                                else
                                    % error aqui
                                end
                            case 'Focus'
                                % Default: 'prediction'
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, 'simulation') || strcmp(value, 'prediction') ||...
                                        strcmp(value, 'stability'))
                                    opt.Focus = value;
                                elseif ~isempty(str2num(value)')  % Passband row vector                                    %
                                    % SISO filter and weighting vector are not considered. TODO!!
                                    opt.Focus = str2num(value)';
                                else
                                    % error aqui
                                end
                            case 'EstCovar'
                                % Default: 'true'if (strcmp(name, 'MOESP') || strcmp(name, 'CVA') ||...
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, 'true') || strcmp(value, 'false'))
                                    opt.EstCovar = value;
                                else
                                    % error aqui
                                end
                            case 'Display'
                                % Default: 'off'
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, 'on') || strcmp(value, 'off'))
                                    opt.Display = value;
                                else
                                    % error aqui
                                end
                            case 'InputOffset'
                                % Default: []
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, '[]') ||...
                                        ~isempty(str2num(value)'))
                                    opt.InputOffset = str2num(value)';
                                    
                                else
                                    % error aqui
                                end
                            case 'OutputOffset'
                                % Default: []
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, '[]') ||...
                                        ~isempty(str2num(value)'))
                                    opt.OutputOffset = str2num(value)';
                                    
                                else
                                    % error aqui
                                end
                            case 'OutputWeight'
                                % Default: []
                                value = optValues{floor(k/2)+1};
                                if (strcmp(value, '[]') ||...
                                        ~isempty(str2num(value)'))
                                    opt.OutputWeight = str2num(value)';
                                else
                                    % error aqui
                                end
                            case 'Advanced'
                                % Default: 250000
                                if isnumeric(value)opt{k+1} = value;
                                    opt.Advanced = value;
                                else
                                    % error aqui
                                end
                        end
                    end
                end
            case 'arx'
                opt = arxOptions;
            case {'armax','arimax'}
                opt = armaxOptions;
        end
    end


    function writeInFile(fileName, textToWrite)
        % Write into a file. Usually a log file
        fileID = fopen(fileName, 'a');
        fprintf(fileID, textToWrite);
        fclose (fileID );
    end

end
