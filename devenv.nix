{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  languages.python = {
    enable = true;
    version = "3.11.9";
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };
  dotenv.enable = true;
}
