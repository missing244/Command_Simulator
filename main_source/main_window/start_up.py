import os, uuid, package.file_operation as file_IO

OLD_BDX_PATH = os.path.join("main_source", "package")
if os.path.isdir(OLD_BDX_PATH) : file_IO.delete_all_file(OLD_BDX_PATH)

OLD_LocalServer_PATH = os.path.join("html_output")
if os.path.isdir(OLD_LocalServer_PATH) : file_IO.delete_all_file(OLD_LocalServer_PATH)

OLD_Parser_PATH = os.path.join("main_source", "bedrock_edition", "command_class", "parser")
if os.path.isdir(OLD_Parser_PATH) : file_IO.delete_all_file(OLD_Parser_PATH)

OLD_Example_PATH = os.path.join("functionality", "example")
if os.path.isdir(OLD_Example_PATH) : file_IO.delete_all_file(OLD_Example_PATH)

OLD_CBStructure_PATH = os.path.join("functionality", "CB_Structure")
NEW_CBStructure_PATH = os.path.join("functionality", "[MAIN]CB_Structure")
if os.path.isdir(OLD_CBStructure_PATH) : os.rename(OLD_CBStructure_PATH, NEW_CBStructure_PATH)

def StartUP() :
    First_Load_Build_Dir = (
        "save_world", 
        "expand_pack", 
        os.path.join("functionality", "Example"),
        os.path.join("functionality", "[MAIN]CB_Structure"),
    )
    [os.makedirs(i, exist_ok=True) for i in First_Load_Build_Dir]

    manifest_json = """
    {
        "format_version": 2,
        "header": {
          "uuid": "%s",
          "name": "example_bp",
          "version": [0, 0, 1],
          "description": "This is a example behavior pack",
          "min_engine_version": [1, 21, 0]
        },
        "modules": [
            {
                "type": "data",
                "description": "子资源包简介",
                "uuid": "%s",
                "version": [0, 0, 1]
            },
            {
                "type": "script",
                "language": "javascript",
                "uuid": "%s",
                "entry": "scripts/Main.js",
                "version": [0, 0, 1]
            }
        ],
        "dependencies": [
            {"module_name": "@minecraft/server", "version": "1.19.0"}
        ]
    }
    """%(uuid.uuid4(), uuid.uuid4(), uuid.uuid4())
    mcfunction_content = "say HelloWorld"
    scriptAPI_content = "\n".join( [
        '//查看API: https://learn.microsoft.com/lt-lt/minecraft/creator/scriptapi/minecraft/server/minecraft-server?view=minecraft-bedrock-stable',
        'import { world, system } from "@minecraft/server"',
        'system.runTimeout( () => {',
        '    const OverWorld = world.getDimension("overworld")',
        '    OverWorld.runCommand("kill @e")',
        '    world.sendMessage("hello world")',
        '})'
    ])
    manifest_path = os.path.join("functionality", "Example", "example_bp")
    manifest_json_path = os.path.join(manifest_path, "manifest.json")
    mcfunc_path = os.path.join(manifest_path, "functions")
    mcfunc_main_path = os.path.join(mcfunc_path, "main.mcfunction")
    scripts_path = os.path.join(manifest_path, "scripts")
    scripts_main_path = os.path.join(scripts_path, "Main.js")
    os.makedirs(manifest_path, exist_ok=True)
    os.makedirs(mcfunc_path, exist_ok=True)
    os.makedirs(scripts_path, exist_ok=True)
    if not os.path.isfile(manifest_json_path) : 
       with open(manifest_json_path, "w+", encoding="utf-8") as _f : _f.write(manifest_json)
    if not os.path.isfile(mcfunc_main_path) : 
       with open(mcfunc_main_path, "w+", encoding="utf-8") as _f : _f.write(mcfunction_content)
    if not os.path.isfile(scripts_main_path) : 
       with open(scripts_main_path, "w+", encoding="utf-8") as _f : _f.write(scriptAPI_content)
StartUP()
