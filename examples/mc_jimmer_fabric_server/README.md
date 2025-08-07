## Fabric base

Create a fabric base image called mc_jimmer_fabric:1.21.8 

## Files 
```
├── config                 # these are base minecraft configurations. Things like server.properties or eula.txt. This is not mod configs. 99 % of the time they all get installed to  /home/mc in the container. 
├── datapacks              # These are the datapacks for the server in zip's please see entrypoint.sh code on how we handle these and how to use them 
├── entrypoint.sh          # this is the base entry point this is hear for other layers to use as this is a bse fabric image.
├── mc_jimmer_fabric.yml   # The configurations file for running container craft. 
├── mod_config             # This holds all mod or plugin configurations that you want installed to /home/mc/config
├── mods                   # local mods that are unavilable any other way. 99% of the time this is un true as you can define local mods in the yaml 
└── README.md              # what you are reading. 

```
