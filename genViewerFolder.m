function [outputArg1,outputArg2] = genViewerFolder(inputFile,varargin)
%% Parse input.
p = inputParser;
p.addOptional('inputFile',[],@(x) ischar(x));
p.addParameter('OutputFile',[],@ischar);
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
    [path,~,~] = fileparts(Inputs.inputFile);
    [file,path] = uiputfile('.json','Save as..',path);
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

%% Write swcs.

%% get Area's
ind = find(Session.visibleStructures);
anatomy = struct();
counter = 0;
for iArea = 1:length(ind)
   cArea = ind(iArea);
   if cArea~=712
       counter = counter+1;
       anatomy(counter).acronym = allenMesh(cArea).acronym;
       anatomy(counter).color = Session.structProps(iArea).FaceColor;
   end
end

%% Join
data = struct('neurons',neurons,...
    'anatomy',anatomy);

%% Write.
text = jsonencode(data);
fid = fopen(Inputs.OutputFile,'w');
fprintf(fid,text);
fclose(fid);

end

