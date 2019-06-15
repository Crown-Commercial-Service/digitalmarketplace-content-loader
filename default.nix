argsOuter@{...}:
let
  # specifying args defaults in this slightly non-standard way to allow us to include the default values in `args`
  args = rec {
    pkgs = import <nixpkgs> {};
    pythonPackages = pkgs.python36Packages;
    forDev = true;
    localOverridesPath = ./local.nix;
  } // argsOuter;
in (with args; {
  digitalMarketplaceContentLoaderEnv = (pkgs.stdenv.mkDerivation rec {
    name = "digitalmarketplace-content-loader-env";
    shortName = "dm-ctnt-ld";
    buildInputs = [
      pythonPackages.python
      pkgs.glibcLocales
      pkgs.libffi
      pkgs.openssl
      pkgs.git
    ] ++ pkgs.stdenv.lib.optionals forDev ([
      ] ++ pkgs.stdenv.lib.optionals pkgs.stdenv.isDarwin [
      ]
    );

    hardeningDisable = pkgs.stdenv.lib.optionals pkgs.stdenv.isDarwin [ "format" ];

    VIRTUALENV_ROOT = (toString (./.)) + "/venv${pythonPackages.python.pythonVersion}";
    VIRTUAL_ENV_DISABLE_PROMPT = "1";
    SOURCE_DATE_EPOCH = "315532800";

    # if we don't have this, we get unicode troubles in a --pure nix-shell
    LANG="en_GB.UTF-8";

    shellHook = ''
      export PS1="\[\e[0;36m\](nix-shell\[\e[0m\]:\[\e[0;36m\]${shortName})\[\e[0;32m\]\u@\h\[\e[0m\]:\[\e[0m\]\[\e[0;36m\]\w\[\e[0m\]\$ "

      if [ ! -e $VIRTUALENV_ROOT ]; then
        ${pythonPackages.python}/bin/python -m venv $VIRTUALENV_ROOT
      fi
      source $VIRTUALENV_ROOT/bin/activate
      make -C ${toString (./.)} requirements${pkgs.stdenv.lib.optionalString forDev "-dev"}
    '';
  }).overrideAttrs (if builtins.pathExists localOverridesPath then (import localOverridesPath args) else (x: x));
})
