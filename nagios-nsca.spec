# TODO
# - update pl
#
# Conditional build:
%bcond_without	mcrypt	# build without mcrypt support
#
Summary:	NSCA daemon for Nagios
Summary(pl):	Demon NSCA dla Nagiosa
Name:		nagios-nsca
Version:	2.6
Release:	1.2
License:	GPL
Group:		Networking
Source0:	http://dl.sourceforge.net/nagios/nsca-%{version}.tar.gz
# Source0-md5:	d526a3ac3c29648c729c5fb4fb332488
Source1:	%{name}.init
Source2:	%{name}.submit
Patch0:		%{name}-groups.patch
Patch1:		%{name}-config.patch
URL:		http://www.nagios.org/
BuildRequires:	autoconf
BuildRequires:	libltdl-devel
%{?with_mcrypt:BuildRequires:	libmcrypt-devel}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	nagios
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir	/var/lib/nagios
%define		_sysconfdir		/etc/nagios

%description
The NSCA addon is designed to accept passive host and service check
results from clients that use the send_nsca utility (also included in
this package) and pass them along to the Nagios process by using the
external command interface. The NSCA daemon can either be run as a
standalone daemon or as a service under inetd. If you have libmcrypt
installed on your systems, you can choose from multiple crypto
algorithms (DES, 3DES, CAST, xTEA, Twofish, LOKI97, RJINDAEL, SERPENT,
GOST, SAFER/SAFER+, etc.) for encrypting the traffic between the
client and the server. Encryption is important in this addon, as it
prevents unauthorized users from sending bogus check results to
Nagios.

%description -l pl
Demon NSCA dla Nagiosa - zbiera wyniki testów ze zdalnych maszyn
(wys³ane przez send_ncsa z pakietu nagios-ncsa-client).

%package client
Summary:	NSCA client
Summary(pl):	Klient NSCA
Group:		Networking

%description client
NSCA client - is used to send service check information from a remote
machine to the NSCA daemon on the central machine that runs Nagios.

%description client -l pl
Klient NSCA - u¿ywany do wysy³ania wyników testów ze zdalnych maszyn
do centralnej maszyny, na której dzia³a Nagios.

%prep
%setup -q -n nsca-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__autoconf}
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/etc/rc.d/init.d,%{_sbindir}}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nagios-nsca
install src/nsca $RPM_BUILD_ROOT%{_sbindir}
install src/send_nsca $RPM_BUILD_ROOT%{_sbindir}

install sample-config/nsca.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nsca.cfg
install sample-config/send_nsca.cfg $RPM_BUILD_ROOT%{_sysconfdir}/send_nsca.cfg

install %{SOURCE2} $RPM_BUILD_ROOT%{_sbindir}/send_nsca-submit
echo '# put your central nagios machine name or address here' > \
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
%attr(755,root,root) %{_sbindir}/send_nsca*
