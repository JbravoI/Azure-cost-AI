param dnsZone string
param lzRegionList array

resource regionSpecificPrivateDnsZone 'Microsoft.Network/privateDnsZones@2018-09-01' = [
  for region in lzRegionList: {
    name: 'privatelink.${region}.${dnsZone}'
    location: 'global'
    tags: {}
    properties: {}
    dependsOn: []
  }
]

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2018-09-01' = [
  for region in lzRegionList: {
    name: 'privatelink.${region}.${dnsZone}/privatelink.${region}.${dnsZone}'
    location: 'global'
    properties: {
      registrationEnabled: false
      virtualNetwork: {
        id: resourceId('${region}-service-group', 'Microsoft.Network/virtualNetworks', 'VNet-PROD-${region}')
      }
    }
    dependsOn:[
      regionSpecificPrivateDnsZone
    ]
  }
]
