\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hmcposter}[2015/03/31 v6.0 HMC Mathematics LaTeX poster class]
\newif\if@clinic
\@clinicfalse
\newif\if@thesis
\@thesisfalse

\DeclareOption{clinic}{\@clinictrue}
\DeclareOption{thesis}{\@thesistrue}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions
\LoadClass{article}
\InputIfFileExists{hmcposter.cfg}{}{}
\RequirePackage{ifthen}
\RequirePackage{mathpazo}
\RequirePackage[scaled=0.95]{helvet}
\renewcommand{\ttdefault}{pcr}
\RequirePackage{sectsty}
\RequirePackage[font=small,font=sf,labelfont=bf]{caption}[2005/06/28]
\RequirePackage{graphics}
\RequirePackage{color}
\definecolor{hmcgold}{cmyk}{0,0.2,0.5,0.3}
\definecolor{hmcorange}{cmyk}{0,0.3,1.0,0}
\definecolor{black}{rgb}{0,0,0}
\definecolor{dkblue}{rgb}{0,0,0.47}
\definecolor{green}{rgb}{0,1,0}
\RequirePackage{multicol}
\setlength{\columnsep}{1in}
\setlength{\columnseprule}{2pt}
\RequirePackage[
centering,
paperwidth=48in,
paperheight=36in,
top=0.5in,
left=1.75in,
right=1.75in,
bottom=2in,
headsep=0.5in,
footskip=0.5in,
marginparwidth=0in,
marginparsep=0in,
includehead,
includefoot,
]{geometry}

\setlength{\parskip}{2ex}

\if@clinic
\geometry{%
headheight=6.0in,
headsep=0.5in,
footskip=1in,
}
\fi

\if@thesis
\geometry{%
headheight=6.5in,
headsep=0.5in,
footskip=1in,
}
\fi
\renewcommand{\LARGE}{\fontsize{72pt}{86pt}\selectfont}
\renewcommand{\Large}{\fontsize{64pt}{72pt}\selectfont}
\renewcommand{\large}{\fontsize{48pt}{60pt}\selectfont}
\renewcommand{\normalsize}{\fontsize{36pt}{44pt}\selectfont}
\renewcommand{\small}{\fontsize{30pt}{36pt}\selectfont}
\renewcommand{\footnotesize}{\fontsize{24pt}{30pt}\selectfont}

\if@clinic
\def\sponsor#1{\gdef\@sponsor{#1}}
\def\@sponsor{\@latex@warning@no@line{No \noexpand\sponsor given}}

\def\sponsorlogo#1{\gdef\@sponsorlogo{#1}}
\def\@sponsorlogo{\@latex@warning@no@line{No \noexpand\sponsorlogo given}}

\def\sponsorlogowidth#1{\gdef\@sponsorlogowidth{#1}}
\def\@sponsorlogowidth{2in}
\fi

\if@thesis
\def\class#1{\gdef\@class{#1}}
\def\@class{\@latex@warning@no@line{No \noexpand\class given}}

\providecommand{\advisor}[1]{%
  \gdef\@advisor{#1}}

\providecommand{\reader}[1]{%
  \gdef\@reader{#1}}
\fi

\def\department#1{\gdef\@department{#1}}
\def\@department{\@latex@warning@no@line{No \noexpand\department given}}
\def\@department{\@latex@warning@no@line{No \noexpand\department given}}

\def\posteryear#1{\gdef\@posteryear{#1}}
\def\@posteryear{\@latex@warning@no@line{No \noexpand\posteryear given}}

\if@clinic
\providecommand{\copyrightholder}[1]{%
  \gdef\@copyrightholder{#1}}
\fi


\newlength{\ignored@length}
\newcommand{\set@ess}[1]{%
  \renewcommand{\and}{%
    \global\def\@ess{s}%
  }%
  \global\def\@ess{}%
  \settowidth{\ignored@length}{#1}%
}
\newcommand{\@andcommaspace}{\unskip, }

\DeclareRobustCommand{\@hmclogo}{%
  \begin{minipage}{4in}
    \raisebox{1in}{\resizebox{10in}{!}{\includegraphics{utfpr.pdf}}}
  \end{minipage}
}
\RequirePackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}                     
\if@clinic
\fancyhead[L]{\raisebox{1.5in}{\@hmclogo}}

\ifthenelse{\isundefined\@sponsorlogo}{}{%
  \fancyhead[R]{\resizebox{!}{\@sponsorlogowidth}{%
      \includegraphics{\@sponsorlogo}}}}
\fi

\if@thesis
\fancyhead[L]{\raisebox{2in}{\@hmclogo}}
\fi

\if@clinic
\fancyhead[C]{%
  \begin{center}
    \color{black}\Large\textsf{\@posteryear\ \@sponsor\ \@department\ Clinic}\\%
    \color{hmcorange}\fontsize{100pt}{120pt}\selectfont\textsf{\textbf{\@title}}
  \end{center}
}
  \fi

\if@thesis
\fancyhead[C]{%
  \begin{center}
    {\color{black}\Large\textsf{\@class}\\}%
    {\color{hmcorange}\fontsize{100pt}{100pt}\selectfont\textsf{\textbf{\@title}}\\[0.25em]}
    {\color{black}\Large\textsf{\@author}\\[-0.5em]}
  \end{center}
}
\fi

\fancyfoot[R]{%
  \ifthenelse{\isundefined{\@copyrightholder}}%
  {}% Do nothing.
  {\textcolor{black}{Copyright \copyright{}~\@posteryear\
      \@copyrightholder}}
}
\fancyfoot[L]{%
  \ifthenelse{\isundefined{\@advisor}}%
  {}% Do nothing.
  {\textcolor{black}{%
      \set@ess{\@advisor}%
      \textbf{Advisor\@ess: }%
      \global\let\and\@andcommaspace%
      \@advisor%
    }
  }%
  \ifthenelse{\isundefined{\@reader}}%
  {}% Do nothing.
  {\textcolor{black}{%
      \set@ess{\@reader}%
      \\\textbf{Reader\@ess: }%
      \global\let\and\@andcommaspace%
      \@reader%
    }
  }
}
\renewcommand{\headrulewidth}{5pt}
\renewcommand{\footrulewidth}{\headrulewidth}

\newcommand{\@rulecolor}{hmcorange}

\if@thesis
\renewcommand{\@rulecolor}{hmcorange}
\fi

\renewcommand{\footrule}{{\color{\@rulecolor}\if@fancyplain\let\footrulewidth\plainfootrulewidth\fi
    \vskip-\footruleskip\vskip-\footrulewidth
    \hrule\@width\headwidth\@height\footrulewidth\vskip\footruleskip}}
\renewcommand{\headrule}{{\color{\@rulecolor}\if@fancyplain\let\headrulewidth\plainheadrulewidth\fi
    \hrule\@height\headrulewidth\@width\headwidth \vskip-\headrulewidth}}

\renewcommand{\page@sofar}{%
   \process@cols\mult@rightbox
       {\ifvoid\count@
          \setbox\count@\hbox to\hsize{}%
        \else
          \wd\count@\hsize
        \fi}%
   \mult@info\z@
    {Column spec:\MessageBreak
       (\the\multicol@leftmargin\space -->
        \the\full@width\space = \the\hsize
        \space x \the\col@number)%
     }%
\ifvmode\else\errmessage{Multicol Error}\fi
   \moveright\multicol@leftmargin
    \hbox to\full@width{%
     \process@cols\mult@gfirstbox{\box\count@
       \hss{\color{\@rulecolor}\vrule\@width\columnseprule}\hss}%
     \box\mult@rightbox
      \rlap{\phantom p}%
    }%
}
\newenvironment{poster}{%
\raggedcolumns
\raggedbottom
\raggedright
\thispagestyle{fancy}
\begin{multicols*}{2}
}%
{\end{multicols*}
}


\renewenvironment{figure}
               {\def\@captype {figure}}
               {}

\renewenvironment{table}
               {\def\@captype {table}}
               {}

\allsectionsfont{\sffamily}

\renewcommand{\@seccntformat}[1]{\relax}

\endinput
