# TODO
# - do something with using_alternate_dump_file in nagios initscript (warn or dump to pipe on startup)
# - do we need to support MAX_PLUGINOUTPUT_LENGTH=4096 for compat of unpatched 2.9? current 512 compat is not even working
#
# Conditional build:
%bcond_without	mcrypt	# build without mcrypt support

Summary:	NSCA daemon for Nagios
Summary(pl.UTF-8):	Demon NSCA dla Nagiosa
Name:		nagios-nsca
Version:	2.9.1
Release:	3
License:	GPL v2+
Group:		Networking
Source0:	http://downloads.sourceforge.net/nagios/nsca-%{version}.tar.gz
# Source0-md5:	3fe2576a8cc5b252110a93f4c8d978c6
Source1:	%{name}.init
Source2:	%{name}.submit
Source3:	nsca-command.cfg
Patch0:		%{name}-groups.patch
Patch1:		%{name}-config.patch
Patch2:		nsca-2.9-fix_open_missing_arg.patch
Patch3:		missing-respect-debug.patch
URL:		http://exchange.nagios.org/directory/Addons/Passive-Checks/NSCA--2D-Nagios-Service-Check-Acceptor/details
BuildRequires:	autoconf
BuildRequires:	libltdl-devel
%{?with_mcrypt:BuildRequires:	libmcrypt-devel}
BuildRequires:	rpmbuild(macros) >= 1.553
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/lib/nagios
%define		_sysconfdir		/etc/nagios

%description
The NSCA addon is designed to accept passive host and service check
results from clients that use the send_nsca utility (included in
client subpackage) and pass them along to the Nagios process by using
the external command interface. The NSCA daemon can either be run as a
standalone daemon or as a service under inetd. If you have libmcrypt
installed on your systems, you can choose from multiple crypto
algorithms (DES, 3DES, CAST, xTEA, Twofish, LOKI97, RJINDAEL, SERPENT,
GOST, SAFER/SAFER+, etc.) for encrypting the traffic between the
client and the server. Encryption is important in this addon, as it
prevents unauthorized users from sending bogus check results to
Nagios.

%description -l pl.UTF-8
Dodatek NSCA służy do przyjmowania wyników pasywnych testów hostów i
usług od klientów używających narzędzia send_nsca (zawartego w
podpakiecie client) i przekazywanai ich do procesu Nagiosa poprzez
interfejs zewnętrznych poleceń. Demon NSCA może działać jako
samodzielny demon albo usługa inetd. Korzystając z biblioteki
libmcrypt można używać wybrać jeden z wielu algorytmów
kryptograficznych (DES, 3DES, CAST, xTEA, Twofish, LOKI97, RJINDAEL,
SERPENT, GOST, SAFER/SAFER+ itp.) do szyfrowania ruchu między klientem
a serwerem. Szyfrowanie jest istotne, jako że zapobiega wysyłaniu do
Nagiosa fałszywych wyników testów przez nieautoryzowanych
użytkowników.

%package client
Summary:	NSCA client
Summary(pl.UTF-8):	Klient NSCA
Group:		Networking

%description client
NSCA client - is used to send service check information from a remote
machine to the NSCA daemon on the central machine that runs Nagios.

%description client -l pl.UTF-8
Klient NSCA - używany do wysyłania wyników testów ze zdalnych maszyn
do centralnej maszyny, na której działa Nagios.

%prep
%setup -q -n nsca-%{version}
%undos -f c
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1

%build
%{__autoconf}
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/plugins,/etc/rc.d/init.d,%{_sbindir}}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nagios-nsca
install -p src/nsca $RPM_BUILD_ROOT%{_sbindir}
install -p src/send_nsca $RPM_BUILD_ROOT%{_sbindir}

cp -p sample-config/nsca.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nsca.cfg
cp -p sample-config/send_nsca.cfg $RPM_BUILD_ROOT%{_sysconfdir}/send_nsca.cfg

install -p %{SOURCE2} $RPM_BUILD_ROOT%{_sbindir}/send_nsca-submit
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/plugins/nsca.cfg
echo '# Put your central Nagios machine name or address here' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/send_nsca-central

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add nagios-nsca
%service nagios-nsca restart "NSCA daemon"

%preun
if [ "$1" = "0" ]; then
	%service nagios-nsca stop
	/sbin/chkconfig --del nagios-nsca
fi

%files
%defattr(644,root,root,755)
%doc Changelog README SECURITY
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nsca.cfg
%attr(755,root,root) %{_sbindir}/nsca
%attr(754,root,root) /etc/rc.d/init.d/nagios-nsca

%files client
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not group md5 mtime size) %{_sysconfdir}/send_nsca.cfg
%attr(640,root,nagios) %config(noreplace) %verify(not group md5 mtime size) %{_sysconfdir}/send_nsca-central
%attr(640,root,nagios) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/plugins/nsca.cfg
%attr(755,root,root) %{_sbindir}/send_nsca
%attr(755,root,root) %{_sbindir}/send_nsca-submit
