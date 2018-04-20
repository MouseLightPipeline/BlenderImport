function [outputArg1,outputArg2] = convViewerSession(inputFile,varargin)
%% Parse input.
p = inputParser;
p.addOptional('inputFile',[],@(x) ischar(x));
p.addParameter('OutputFile',[],@ischar);
p.addParameter('AxonWidth',15,@(x) isnumeric(x) && length(x) == 1);
p.addParameter('DendriteWidth',20,@(x) isnumeric(x) && length(x) == 1);
p.addParameter('MeshFile',fullfile('//dm11/mousebrainmicro/Allen_compartments/Matlab/allenMeshCorrectedAxis.mat'),@(x) ischar(x));
p.parse(varargin{:});
Inputs = p.Results;

%% Check if output/ input file provided.
if isempty(Inputs.inputFile)
    [file,path] = uigetfile('.mat','Open Reconstruction Viewer file');
    if path==0
        return
    end
    Inputs.inputFile = fullfile(path,file);
end

if isempty(Inputs.OutputFile)
    [file,path] = uiputfile('.json','Save as..');
    if path==0
        return
    end
    Inputs.OutputFile = fullfile(path,file);
end


%% Load session.
fprintf('\nLoading Session..');
load(Inputs.inputFile);

%% Get anatomy Info.
fprintf('\nLoading Anatomy Info..');
load(Inputs.MeshFile);

%% get Neurons.
names = {Session.Neurons.Name};
names = cellfun(@(x) x(1:6),names,'UniformOutput',false);
[names,ind,~] = unique(names);

neurons = struct('id','','color',[]);
for i =1:size(names,2)
    cNeuron = ind(i);
    name = names{i};
    color = Session.Neurons(cNeuron).Color;
   neurons(i).id = name;
   neurons(i).color = color;
end

%% get Area's
ind = find(Session.visibleStructures);
ind = ind(ind~=712);
anatomy = struct();
cMap = hsv(length(ind));
for iArea = 1:length(ind)
   cArea = ind(iArea);
   anatomy(iArea).acronym = allenMesh(cArea).acronym;
   anatomy(iArea).color = cMap(iArea,:);
end

%% create settings.
settings = struct('axonWidth',Inputs.AxonWidth,...
    'dendWidth',Inputs.AxonWidth);

%% Join
data = struct('settings',settings,...
    'neurons',neurons,...
    'anatomy',anatomy);

%% Write.
text = jsonencode(data);
fid = fopen(Inputs.OutputFile,'w');
fprintf(fid,text);
fclose(fid);

end

