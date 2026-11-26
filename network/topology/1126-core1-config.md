# Core1 설정 요약 · 2026-11-26

당일 콘솔 기록에서 확인한 설정 요소를 정리했다. 아래 명령은 공개용 재현 예시이며 원본 running-config가 아니다. 주소는 변수 또는 예시로 표시한다.

```text
spanning-tree mode rapid-pvst
ip routing
vlan 10
vlan 20
vlan 30
vlan 40
vlan 901
!
interface Vlan10
 ip address <CORE1_VLAN10_IP> <MASK>
 standby version 2
 standby 10 ip <VLAN10_VIP>
 standby 10 priority 110
 standby 10 preempt
 no shutdown
!
! VLAN 20/30/40/901에도 각 그룹과 해당 VIP 적용
interface GigabitEthernet0/3
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,901
!
interface GigabitEthernet1/0
 shutdown
!
ip route 0.0.0.0 0.0.0.0 <ASA_INSIDE_NEXT_HOP>
```

원본 설정 적용 및 저장은 당일 기록 기준. 이 예시 전체를 별도로 실행한 것은 아니다. VLAN 901의 실제 priority/최종 Active 여부는 재검증한다.

## 다음 검증 명령
```text
show ip interface brief
show standby brief
show interfaces trunk
show vlan brief
show ip route
show mac address-table
show logging
```
