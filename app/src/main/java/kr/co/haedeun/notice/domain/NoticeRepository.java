package kr.co.haedeun.notice.domain;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface NoticeRepository extends JpaRepository<Notice, Long> {

    @Query("""
            select n from Notice n
            where n.hidden = false
              and (:category is null or n.category = :category)
              and (:q is null or lower(n.title) like lower(concat('%', :q, '%'))
                              or lower(n.content) like lower(concat('%', :q, '%')))
            order by n.pinned desc, n.createdAt desc, n.id desc
            """)
    Page<Notice> search(@Param("category") Category category, @Param("q") String q, Pageable pageable);

    long countByHiddenFalse();
}
