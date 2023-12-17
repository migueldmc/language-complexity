{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-22.11") {} }:
  let python-packages = ps: with ps; [
    black
    ipywidgets
    jupyterlab
    matplotlib
    nltk
    numpy
    openpyxl
    pandas
    xarray
  ];
  in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
    	(python3.withPackages python-packages)
    ];
  }

