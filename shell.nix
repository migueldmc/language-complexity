{ pkgs ? import <nixpkgs> {} }:
  let python-packages = ps: with ps; [
    black
    ipywidgets
    jupyterlab
    matplotlib
    nltk
    numpy
    openpyxl
    pandas
  ];
  in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
    	(python3.withPackages python-packages)
    ];
  }

