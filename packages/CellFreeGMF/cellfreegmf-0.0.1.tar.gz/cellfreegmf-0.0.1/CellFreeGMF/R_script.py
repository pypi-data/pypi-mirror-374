DESeq2_function = '''
DESeq2_function <- function(counts_df, group_vector, volcano_plot = FALSE, file_path = NULL){{
    suppressMessages(library(DESeq2))
    suppressMessages(library(org.Hs.eg.db))
    suppressMessages(library(dplyr))
    suppressMessages(library(ggplot2))
    suppressMessages(library(ggrepel))

    recode_data <- recode(group_vector, `1` = "Tumor", `0` = "Normal")
    col_data <- data.frame(
        condition = factor(recode_data),
        row.names = rownames(group_vector)
    )
    
    #col_data <- data.frame(condition = factor(group_vector))
    # print(head(col_data))

    ## run Deseq2 & extract results
    dds <- DESeqDataSetFromMatrix(countData = counts_df,
                                colData = col_data,
                                design = ~ condition)
    dds <- DESeq(dds)
    res <- results(dds, contrast = c('condition', 'Tumor', 'Normal'))

    res_df <- as.data.frame(res)

    if(volcano_plot){
        target_degs <- res_df %>%
        mutate(significance = case_when(
            padj < 0.05 & log2FoldChange > 0.25 ~ "Upregulated",
            padj < 0.05 & log2FoldChange < -0.25 ~ "Downregulated",
            TRUE ~ "Not Significant"
        ))
        target_gene_emsemble <- sub("\\\\..*","",rownames(target_degs))
        gene <- mapIds(
            org.Hs.eg.db,
            keys = target_gene_emsemble,       # 输入的 Ensembl IDs
            keytype = "ENSEMBL",      # 输入ID类型（Ensembl ID）
            column = "SYMBOL",      # 要转换的目标ID类型（Entrez ID）
            multiVals = "filter"      # 处理多匹配的方式："filter"（默认，返回第一个匹配）
        )
        # print(gene)
        target_degs$gene <- NA
        target_degs[names(gene), ]$gene <- gene

        # print(head(target_degs))

        ###绘图——基础火山图###
        cut_off_FDR =0.05 #设置FDR的阈值
        cut_off_log2FC =0.25 #设置log2FC的阈值

        p1 <- ggplot(target_degs, aes(x =log2FoldChange, y=-log10(padj), colour=significance)) + #x、y轴取值限制，颜色根据"Sig"
            geom_point(alpha=0.65, size=2) +  #点的透明度、大小
            scale_color_manual(values=c("#546de5", "#d2dae2","#ff4757")) + xlim(c(-2.5, 2.5)) +  #调整点的颜色和x轴的取值范围
            geom_vline(xintercept=c(-cut_off_log2FC,cut_off_log2FC),lty=4,col="black",lwd=0.8) + #添加x轴辅助线,lty函数调整线的类型："twodash"、"longdash"、"dotdash"、"dotted"、"dashed"、"solid"、"blank"
            geom_hline(yintercept = -log10(cut_off_FDR), lty=4,col="black",lwd=0.8) +  #添加y轴辅助线
            labs(title = "Volcano Plot",
                x = "Log2 Fold Change",
                y = "-Log10 Adjusted P-value",
                color = "Significance") +
            theme_bw() + # 主题，help(theme)查找其他个性化设置
            theme(plot.title = element_text(hjust = 0.5),
                    legend.position="right", 
                    legend.title = element_blank()
            ) 

        p3 <- p1 + geom_label_repel(
            data = subset(target_degs, target_degs$padj < cut_off_FDR & abs(target_degs$log2FoldChange) >= cut_off_log2FC),# 可以设置跟上面不同的阈值，用数值替换即可
            aes(label = gene), size = 3,max.overlaps = getOption("ggrepel.max.overlaps", default = 30),
            fill="#CCFFFF" )
        if(is.null(file_path)){
            ggsave(file = './volcano_plot.pdf', plot = p3, width = 6, height = 5)
        }else{
            ggsave(file = paste0(file_path, '/volcano_plot.pdf', sep=""), plot = p3, width = 6, height = 5)
        }
        
    
    }

    return(res_df)
}}
'''

DESeq2_standard = '''
DESeq2_standard <- function(counts_matrix){
    suppressMessages(library(DESeq2))
    suppressMessages(library(dplyr))
    counts_matrix_norm <- DESeq2::varianceStabilizingTransformation(as.matrix(counts_matrix)) %>% data.frame() 

    return(counts_matrix_norm)
}
'''

limma_function = '''
limma_function <- function(counts_df, group_vector, volcano_plot = FALSE, file_path = NULL){
    suppressMessages(library(limma))
    suppressMessages(library(dplyr))
    suppressMessages(library(org.Hs.eg.db))
    suppressMessages(library(ggplot2))
    suppressMessages(library(ggrepel))

    recode_data <- recode(group_vector, `1` = "Tumor", `0` = "Normal")
    group <- factor(recode_data)

    design <- model.matrix(~0 + group)
    colnames(design) <- levels(group)

    fit <- lmFit(counts_df, design)

    contrast.matrix <- makeContrasts(Tumor-Normal, levels=design)

    fit2 <- contrasts.fit(fit, contrast.matrix)
    fit2 <- eBayes(fit2)

    results <- topTable(fit2, number=Inf, adjust.method="BH")

    # print(head(results))

    if(volcano_plot){
        target_degs <- results %>%
        mutate(significance = case_when(
            adj.P.Val < 0.05 & logFC > 0.25 ~ "Upregulated",
            adj.P.Val < 0.05 & logFC < -0.25 ~ "Downregulated",
            TRUE ~ "Not Significant"
        ))
        target_gene_emsemble <- sub("\\\\..*","",rownames(target_degs))
        gene <- mapIds(
            org.Hs.eg.db,
            keys = target_gene_emsemble,       # 输入的 Ensembl IDs
            keytype = "ENSEMBL",      # 输入ID类型（Ensembl ID）
            column = "SYMBOL",      # 要转换的目标ID类型（Entrez ID）
            multiVals = "filter"      # 处理多匹配的方式："filter"（默认，返回第一个匹配）
        )
        # print(gene)
        target_degs$gene <- NA
        target_degs[names(gene), ]$gene <- gene

        # print(head(target_degs))

        ###绘图——基础火山图###
        cut_off_FDR =0.05 #设置FDR的阈值
        cut_off_log2FC =0.25 #设置log2FC的阈值

        p1 <- ggplot(target_degs, aes(x =logFC, y=-log10(adj.P.Val), colour=significance)) + #x、y轴取值限制，颜色根据"Sig"
            geom_point(alpha=0.65, size=2) +  #点的透明度、大小
            scale_color_manual(values=c("#546de5", "#d2dae2","#ff4757")) + xlim(c(-2.5, 2.5)) + ylim(c(0, 10)) +  #调整点的颜色和x轴的取值范围
            geom_vline(xintercept=c(-cut_off_log2FC,cut_off_log2FC),lty=4,col="black",lwd=0.8) + #添加x轴辅助线,lty函数调整线的类型："twodash"、"longdash"、"dotdash"、"dotted"、"dashed"、"solid"、"blank"
            geom_hline(yintercept = -log10(cut_off_FDR), lty=4,col="black",lwd=0.8) +  #添加y轴辅助线
            labs(title = "Volcano Plot",
                x = "Log2 Fold Change",
                y = "-Log10 Adjusted P-value",
                color = "Significance") +
            theme_bw() + # 主题，help(theme)查找其他个性化设置
            theme(plot.title = element_text(hjust = 0.5),
                    legend.position="right", 
                    legend.title = element_blank()
            ) 

        p3 <- p1 + geom_label_repel(
            data = subset(target_degs, target_degs$adj.P.Val < cut_off_FDR & abs(target_degs$logFC) >= cut_off_log2FC),# 可以设置跟上面不同的阈值，用数值替换即可
            aes(label = gene), size = 3,
            fill="#CCFFFF" )
        if(is.null(file_path)){
            ggsave(file = './volcano_plot.pdf', plot = p3, width = 6, height = 5)
        }else{
            ggsave(file = paste0(file_path, '/volcano_plot.pdf', sep=""), plot = p3, width = 6, height = 5)
        }
    }
    
    return(results)
}
'''

GOSemSim_function = '''
GOSemSim_function <- function(target_gene, cell_gene, target_gene_type='SYMBOL', cell_gene_type = 'ENSEMBL'){
    suppressMessages(library(GOSemSim))
    suppressMessages(library(org.Hs.eg.db))
    suppressMessages(library(dplyr))

    print(R.home())
    print(.libPaths())

    if(target_gene_type == 'SYMBOL'){
        target_gene <- mapIds(
            org.Hs.eg.db,
            keys = target_gene,      # 输入的Gene Symbols
            keytype = "SYMBOL",       # 输入ID类型（Gene Symbol）
            column = "ENTREZID",      # 要转换的目标ID类型（Entrez ID）
            multiVals = "filter"      # 处理多匹配的方式："filter"（只返回第一个匹配）
        )
    }else if(target_gene_type == 'ENSEMBL'){
        target_gene <- mapIds(
            org.Hs.eg.db,
            keys = target_gene,       # 输入的 Ensembl IDs
            keytype = "ENSEMBL",      # 输入ID类型（Ensembl ID）
            column = "ENTREZID",      # 要转换的目标ID类型（Entrez ID）
            multiVals = "filter"      # 处理多匹配的方式："filter"（默认，返回第一个匹配）
        )
    }

    if(cell_gene_type == 'SYMBOL'){
        for(i in 1:length(cell_gene)){
            cell_gene[[i]] <- mapIds(
                org.Hs.eg.db,
                keys = cell_gene[[i]],      # 输入的Gene Symbols
                keytype = "SYMBOL",       # 输入ID类型（Gene Symbol）
                column = "ENTREZID",      # 要转换的目标ID类型（Entrez ID）
                multiVals = "filter"      # 处理多匹配的方式："filter"（只返回第一个匹配）
            )                
        }
    }else if(cell_gene_type == 'ENSEMBL'){
        for(i in 1:length(cell_gene)){
            cell_gene[[i]] <- mapIds(
                org.Hs.eg.db,
                keys = cell_gene[[i]],       # 输入的 Ensembl IDs
                keytype = "ENSEMBL",      # 输入ID类型（Ensembl ID）
                column = "ENTREZID",      # 要转换的目标ID类型（Entrez ID）
                multiVals = "filter"      # 处理多匹配的方式："filter"（默认，返回第一个匹配）
            )
        }
    }

    hsGO_BP <- godata('org.Hs.eg.db', ont="BP")
    hsGO_MF <- godata('org.Hs.eg.db', ont="MF")
    hsGO_CC <- godata('org.Hs.eg.db', ont="CC")

    BP_sim_matrix <- matrix(0, nrow=length(target_gene), ncol=length(cell_gene))
    MF_sim_matrix <- matrix(0, nrow=length(target_gene), ncol=length(cell_gene))
    CC_sim_matrix <- matrix(0, nrow=length(target_gene), ncol=length(cell_gene))

    for(i in 1:length(target_gene)){
        cat('All_target_gene:', length(target_gene), ', current_target_gene: ', i, '\t')
        for(j in 1:length(cell_gene)){

            BP_sim_matrix[i, j] <- clusterSim(target_gene[i], 
                                                cell_gene[[j]], 
                                                semData=hsGO_BP, 
                                                measure="Wang", combine="BMA")
            if(is.na(BP_sim_matrix[i, j]) || is.nan(BP_sim_matrix[i, j])){
                BP_sim_matrix[i, j] <- 0
            }

            MF_sim_matrix[i, j] <- clusterSim(target_gene[i], 
                                                cell_gene[[j]], 
                                                semData=hsGO_MF, 
                                                measure="Wang", combine="BMA")
            if(is.na(MF_sim_matrix[i, j]) || is.nan(MF_sim_matrix[i, j])){
                MF_sim_matrix[i, j] <- 0
            }

            CC_sim_matrix[i, j] <- clusterSim(target_gene[i], 
                                                cell_gene[[j]], 
                                                semData=hsGO_CC, 
                                                measure="Wang", combine="BMA")
            if(is.na(CC_sim_matrix[i, j]) || is.nan(CC_sim_matrix[i, j])){
                CC_sim_matrix[i, j] <- 0
            }

        }        
    }

    return(list(BP_sim_matrix, MF_sim_matrix, CC_sim_matrix, target_gene, names(target_gene)))

}
'''