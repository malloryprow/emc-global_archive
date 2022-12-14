program fno_precip
!$$$  main program documentation block
!
! main program: jma_precip    creates grib records for wafs merge
!   prgmmr: Kistler          org: np23        date: 1999-06-11
!
! abstract: converts jan-precip 6 hour records from accumulations since 0 hr 
!	to 6 hour accumulations
! 
! program history log:
!
! usage: 
!
! input file: fort.11  jma precip - 6 hr records are accumulations since hour 0
!
! output file: grib
!   unit 51 -  6 and 12 hour accumulations
!
! subprograms called:
!   baopenr          grib i/o
!   baopenw          grib i/o
!   baclose          grib i/o
!   getgbh            grib reader
!   getgb             grib reader
!   putgb             grib writer
!
! exit states:
!   cond =   0 - successful run
!   cond =   1 - I/O abort
!
! attributes:
!   language: fortran 90
!
!$$$

implicit none
integer ip1,ip2,i,m,jpds5,lunot
integer ifile,index,j,n,ndata,iret,jret,npt,kskp,maxgrd,maxfhr
parameter (maxfhr=120)
integer jpds(200),kpds(200),jgds(200),kgds(200)
real,     allocatable :: rain1(:) 
real,     allocatable :: rain2(:)
logical(1),allocatable :: lbms(:)
character*7 cfortnn

lunot=51
ifile=11
index=0
j=-1
jpds=-1  
jgds=-1

write(cfortnn,'(a5,i2)') 'fort.',ifile
call baopenr(ifile,cfortnn,iret)
if (iret .ne. 0) then; print*,' baopenr ,ifile,iret =',ifile,iret; stop 1; endif
write(cfortnn,'(a5,i2)') 'fort.',index
call getgbh(ifile,index,j,jpds,jgds, ndata,maxgrd,j,kpds,kgds,iret)
if (iret .ne. 0) then; print*,' getgbh ,ifile,index,iret =',ifile,index,iret; stop 1; endif
print*,' maxgrd = ',maxgrd
allocate (lbms(maxgrd),rain1(maxgrd),rain2(maxgrd))

write(cfortnn,'(a5,i2)') 'fort.',lunot
call baopenw(lunot,cfortnn,iret)
if (iret .ne. 0) then; print*,' baopen '//cfortnn//' iret =',iret; stop 1; endif

! loop over total rain accumulation

jpds5=61
iret=0
ip2=0
rain1=0.
do while (ip2.lt.maxfhr ) 
	! read records separated by 6 hours
	ip2=ip2+6
	j=-1
	jpds=-1
	jgds=-1
	jpds(5)=jpds5
	jpds(6)=1
	jpds(7)=0
	jpds(14)=ip2
	jpds(15)=0  
	print*,'read  ',ifile,index,jpds(14),jpds(15),jpds(5)
	call getgb(ifile,index,maxgrd,j,jpds,jgds,ndata,j,kpds,kgds,lbms, &
				rain2,iret)
	if (iret .ne. 0) exit
! write 6hr amounts
!	rain1=rain2-rain1
 	rain1=rain2
	kpds(14)=ip2-6
	kpds(15)=ip2
	kpds(16)=4    
	print*,'write ',kpds(14),kpds(15),kpds(5)
	call putgb(lunot,ndata,kpds,kgds,lbms,rain1,jret) 
	if (jret .ne. 0) call bort(jret)
!	rain1=rain2
enddo
print*,' iret = ',iret,'for ip2 = ',ip2
end
