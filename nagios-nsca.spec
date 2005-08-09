#
# Conditional build:
%bcond_without	mcrypt	# build without mcrypt support
#
Summary:	NSCA daemon for Nagios
Summary(pl):	Demon NSCA dla Nagiosa
Name:		nagios-nsca
Version:	2.4
Release:	2
License:	GPL
Group:		Networking
Source0:	ftp://distfiles.pld-linux.org/src/nsca-%{version}.tar.gz
# Source0-md5:	ab58553a87940f574ec54189a43a70bc
Source1:	%{name}.init
Source2:	%{name}.submit
Patch0:		%{name}-groups.patch
URL:		http://www.nagios.org/
BuildRequires:	autoconf
BuildRequires:	libltdl-devel
%{?with_mcrypt:BuildRequires:	libmcrypt-devel}
PreReq:		nagios
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
NSCA daemon for Nagios - listens for service check results from
remote machines (sent using send_ncsa from nagios-ncsa-client
package).

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

%build
%{__autoconf}
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/nagios,/etc/rc.d/init.d} \
	$RPM_BUILD_ROOT%{_sbindir}

install src/nsca $RPM_BUILD_ROOT%{_sbindir}
sed -e 's@^command_file=.*@command_file=/var/lib/nagios/rw/nagios.cmd@;s@^alternate_dump_file=.*@alternate_dump_file=/var/lib/nagios/rw/nsca.dump@' \
	nsca.cfg > $RPM_BUILD_ROOT%{_sysconfdir}/nagios/nsca.cfg
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/nagios-nsca

install src/send_nsca $RPM_BUILD_ROOT%{_sbindir}
install send_nsca.cfg $RPM_BUILD_ROOT%{_sysconfdir}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sbindir}/send_nsca-submit
echo '# put your central nagios machine name or address here' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/send_nsca-central

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add nagios-nsca
if [ -f /var/lock/subsys/nagios-nsca ]; then
	/etc/rc.d/init.d/nagios-nsca restart >&2
else
	echo "Run \"/etc/rc.d/init.d/nagios-nsca start\" to start NSCA daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/nagios-nsca ]; then
		/etc/rc.d/init.d/nagios-nsca stop >&2
	fi
	/sbin/chkconfig --del nagios-nsca
fi

%files
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/nagios/nsca.cfg
%doc Changelog README SECURITY
%attr(755,root,root) %{_sbindir}/nsca
%attr(754,root,root) /etc/rc.d/init.d/nagios-nsca

%files client
%defattr(644,root,root,755)
%attr(640,root,nagios) %config(noreplace) %verify(not size mtime md5 group) %{_sysconfdir}/send_nsca.cfg
%attr(640,root,nagios) %config(noreplace) %verify(not size mtime md5 group) %{_sysconfdir}/send_nsca-central
%attr(755,root,root) %{_sbindir}/send_nsca*
