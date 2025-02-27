{
  description = "Python environment for gateway";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShells.default = with pkgs;
          mkShell {
            buildInputs = [
              python311
              pipreqs
              python311Packages.virtualenv
              python311Packages.fastapi
              python311Packages.uvicorn
              python311Packages.httpx
              python311Packages.gunicorn
            ];
          };
      }
    );
}
